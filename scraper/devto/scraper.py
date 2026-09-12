import requests
from typing import List

from scraper.base.base_scraper import BaseScraper
from scraper.base.lead_model import Lead
from config.keywords import BUSINESS_KEYWORDS


DEVTO_API = "https://dev.to/api/articles"


class DevToScraper(BaseScraper):

    def __init__(self):
        super().__init__("Dev.to")

    def scrape(self) -> List[Lead]:

        response = requests.get(
            DEVTO_API,
            timeout=10
        )

        response.raise_for_status()

        articles = response.json()

        leads = []

        scanned = 0
        skipped = 0

        for article in articles[:100]:

            scanned += 1

            title = article.get("title", "")
            description = article.get("description", "")

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
                    source="Dev.to",
                    url=article.get("url", ""),
                    posted_at=article.get("published_at", ""),
                    contact_name=article.get("user", {}).get("name", ""),
                    raw_data=article
                )
            )

            if len(leads) >= 20:
                break

        print("DevToScraper:")
        print(f"  Articles Scanned     : {scanned}")
        print(f"  Irrelevant Skipped   : {skipped}")
        print(f"  Business Leads Found : {len(leads)}")

        return leads