import feedparser
from typing import List

from scraper.base.base_scraper import BaseScraper
from scraper.base.lead_model import Lead
from config.keywords import BUSINESS_KEYWORDS


RSS_URL = "https://news.ycombinator.com/rss"


class RSSScraper(BaseScraper):

    def __init__(self):
        super().__init__("RSS")

    def scrape(self) -> List[Lead]:

        feed = feedparser.parse(RSS_URL)

        leads = []

        scanned = 0
        skipped = 0

        for entry in feed.entries[:50]:

            scanned += 1

            title = getattr(entry, "title", "")
            description = getattr(entry, "summary", "")

            combined = f"{title} {description}".lower()

            # Ignore Show HN / Ask HN
            if title.lower().startswith("show hn"):
                skipped += 1
                continue

            if title.lower().startswith("ask hn"):
                skipped += 1
                continue

            # Keep only business-related entries
            if not any(keyword in combined for keyword in BUSINESS_KEYWORDS):
                skipped += 1
                continue

            lead = Lead(
                title=title,
                description=description,
                source="RSS",
                url=getattr(entry, "link", ""),
                posted_at=getattr(entry, "published", ""),
                contact_name=getattr(entry, "author", ""),
                raw_data=dict(entry)
            )

            leads.append(lead)

            if len(leads) >= 10:
                break

        print(f"RSSScraper:")
        print(f"  Articles Scanned     : {scanned}")
        print(f"  Irrelevant Skipped   : {skipped}")
        print(f"  Business Leads Found : {len(leads)}")

        return leads
