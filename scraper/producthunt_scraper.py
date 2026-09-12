import feedparser
import re

from scraper.base_scraper import BaseScraper
from config.keywords import BUSINESS_KEYWORDS

RSS_URL = "https://www.producthunt.com/feed"


class ProductHuntScraper(BaseScraper):

    @staticmethod
    def clean_html(text):
        """Remove HTML tags and normalize whitespace."""
        text = re.sub(r"<[^>]+>", "", text)
        text = text.replace("\n", " ").strip()
        return " ".join(text.split())

    def fetch_leads(self, limit=20):

        try:

            feed = feedparser.parse(RSS_URL)

            leads = []

            scanned = 0
            skipped = 0

            # Scan more entries than required
            for entry in feed.entries[:100]:

                scanned += 1

                title = getattr(entry, "title", "")
                description = self.clean_html(
                    getattr(entry, "summary", "")
                )

                combined = f"{title} {description}".lower()

                # Keep only relevant products
                if not any(keyword in combined for keyword in BUSINESS_KEYWORDS):
                    skipped += 1
                    continue

                leads.append(

                    self.normalize_lead(

                        title=title,

                        description=description,

                        url=getattr(entry, "link", ""),

                        platform="Product Hunt",

                        author=getattr(entry, "author", ""),

                        published_at=getattr(entry, "published", "")

                    )

                )

                if len(leads) >= limit:
                    break

            print("ProductHuntScraper:")
            print(f"  Products Scanned     : {scanned}")
            print(f"  Irrelevant Skipped   : {skipped}")
            print(f"  Business Leads Found : {len(leads)}")

            return leads

        except Exception as e:

            print("Product Hunt Error:", e)

            return []


if __name__ == "__main__":

    scraper = ProductHuntScraper()

    leads = scraper.fetch_leads()

    print(f"\nFetched {len(leads)} quality Product Hunt leads\n")

    for lead in leads:

        print("-" * 60)
        print("Title:", lead["title"])
        print("Author:", lead["author"])
        print("Platform:", lead["platform"])
        print("Published:", lead["published_at"])
        print("URL:", lead["url"])