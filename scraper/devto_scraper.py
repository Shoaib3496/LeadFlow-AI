import requests

from scraper.base_scraper import BaseScraper
from config.keywords import BUSINESS_KEYWORDS

DEVTO_API = "https://dev.to/api/articles"


class DevToScraper(BaseScraper):

    def fetch_leads(self, limit=20):

        try:

            response = requests.get(
                DEVTO_API,
                timeout=10
            )

            response.raise_for_status()

            articles = response.json()

            leads = []

            scanned = 0
            skipped = 0

            # Scan more articles and filter them
            for article in articles[:100]:

                scanned += 1

                title = article.get("title", "")
                description = article.get("description", "")

                combined = f"{title} {description}".lower()

                # Skip articles without business-related keywords
                if not any(keyword in combined for keyword in BUSINESS_KEYWORDS):
                    skipped += 1
                    continue

                leads.append(

                    self.normalize_lead(

                        title=title,

                        description=description,

                        url=article.get("url", ""),

                        platform="Dev.to",

                        author=article.get("user", {}).get("name", ""),

                        published_at=article.get("published_at", "")

                    )

                )

                if len(leads) >= limit:
                    break

            print("DevToScraper:")
            print(f"  Articles Scanned     : {scanned}")
            print(f"  Irrelevant Skipped   : {skipped}")
            print(f"  Business Leads Found : {len(leads)}")

            return leads

        except Exception as e:

            print("Dev.to Error:", e)

            return []


if __name__ == "__main__":

    scraper = DevToScraper()

    leads = scraper.fetch_leads()

    print(f"\nFetched {len(leads)} quality Dev.to leads\n")

    for lead in leads:

        print("-" * 60)
        print("Title:", lead["title"])
        print("Author:", lead["author"])
        print("Platform:", lead["platform"])
        print("Published:", lead["published_at"])
        print("URL:", lead["url"])