import feedparser
import re
from typing import List

from scraper.base.base_scraper import BaseScraper
from scraper.base.lead_model import Lead
from config.keywords import BUSINESS_KEYWORDS


RSS_URL = "https://www.producthunt.com/feed"


class ProductHuntScraper(BaseScraper):

    def __init__(self):
        super().__init__("Product Hunt")

    @staticmethod
    def clean_html(text: str) -> str:
        """Remove HTML tags and normalize whitespace."""
        text = re.sub(r"<[^>]+>", "", text)
        text = text.replace("\n", " ").strip()
        return " ".join(text.split())

    def scrape(self) -> List[Lead]:

        feed = feedparser.parse(RSS_URL)

        leads = []

        scanned = 0
        skipped = 0

        for entry in feed.entries[:100]:

            scanned += 1

            title = getattr(entry, "title", "")
            description = self.clean_html(
                getattr(entry, "summary", "")
            )

            combined = f"{title} {description}".lower()

            if not any(
                keyword in combined
                for keyword in BUSINESS_KEYWORDS
            ):
                skipped += 1
                continue

            leads.append(
                Lead(
                    title=title,
                    description=description,
                    source="Product Hunt",
                    url=getattr(entry, "link", ""),
                    posted_at=getattr(entry, "published", ""),
                    contact_name=getattr(entry, "author", ""),
                    raw_data=dict(entry)
                )
            )

            if len(leads) >= 20:
                break

        print("ProductHuntScraper:")
        print(f"  Products Scanned     : {scanned}")
        print(f"  Irrelevant Skipped   : {skipped}")
        print(f"  Business Leads Found : {len(leads)}")

        return leads