import feedparser

from scraper.base_scraper import BaseScraper
from config.keywords import BUSINESS_KEYWORDS


RSS_URL = "https://news.ycombinator.com/rss"


class RSSScraper(BaseScraper):

    def fetch_leads(self, limit=10):

        try:

            feed = feedparser.parse(RSS_URL)

            leads = []

            scanned = 0
            skipped = 0

            # Scan more entries than needed
            for entry in feed.entries[:50]:

                scanned += 1

                title = getattr(entry, "title", "")
                description = getattr(entry, "summary", "")

                combined = f"{title} {description}".lower()

                # Skip Show HN / Ask HN
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

                leads.append(

                    self.normalize_lead(

                        title=title,

                        description=description,

                        url=getattr(entry, "link", ""),

                        platform="RSS",

                        author=getattr(entry, "author", ""),

                        published_at=getattr(entry, "published", "")

                    )

                )

                if len(leads) >= limit:
                    break

            print("RSSScraper:")
            print(f"  Articles Scanned     : {scanned}")
            print(f"  Irrelevant Skipped   : {skipped}")
            print(f"  Business Leads Found : {len(leads)}")

            return leads

        except Exception as e:

            print("RSS Error:", e)

            return []


if __name__ == "__main__":

    scraper = RSSScraper()

    leads = scraper.fetch_leads()

    print(f"\nFetched {len(leads)} quality RSS leads\n")

    for lead in leads:

        print("-" * 60)
        print("Title:", lead["title"])
        print("Platform:", lead["platform"])
        print("Published:", lead["published_at"])
        print("URL:", lead["url"])
