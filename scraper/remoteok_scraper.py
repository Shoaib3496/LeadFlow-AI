import requests

from scraper.base_scraper import BaseScraper
from config.tech_keywords import TECH_KEYWORDS


REMOTEOK_API = "https://remoteok.com/api"


class RemoteOKScraper(BaseScraper):

    def fetch_leads(self, limit=20):

        leads = []

        scanned = 0
        skipped = 0

        headers = {
            "User-Agent": "LeadFlow-AI"
        }

        try:

            response = requests.get(
                REMOTEOK_API,
                headers=headers,
                timeout=15
            )

            response.raise_for_status()

            jobs = response.json()

            # First element is metadata
            jobs = jobs[1:]

            for job in jobs:

                scanned += 1

                title = job.get("position", "")
                
                title_lower = title.lower()

                if not any(keyword in title_lower for keyword in TECH_KEYWORDS):
                    skipped += 1
                    continue

                company = job.get("company", "")
                description = job.get("description", "") or ""

                combined = f"{title} {description}".lower()

                if not any(
                    keyword in combined
                    for keyword in TECH_KEYWORDS
                ):
                    skipped += 1
                    continue

                priority = 0

                priority_keywords = [
                    "python",
                    "ai",
                    "machine learning",
                    "developer",
                    "software",
                    "automation",
                    "api"
                ]

                for keyword in priority_keywords:
                    if keyword in combined:
                        priority += 10

                leads.append(

                    self.normalize_lead(

                        title=title,

                        description=description[:1000],

                        url=job.get("url", ""),

                        platform="RemoteOK",

                        author=company,

                        published_at=job.get("date", "")

                    )

                )

                if len(leads) >= limit:
                    break

            print("RemoteOKScraper:")
            print(f"  Jobs Scanned         : {scanned}")
            print(f"  Irrelevant Skipped   : {skipped}")
            print(f"  Business Leads Found : {len(leads)}")

            return leads

        except Exception as e:

            print(f"[RemoteOKScraper] Error: {e}")
            return []


if __name__ == "__main__":

    scraper = RemoteOKScraper()

    leads = scraper.fetch_leads()

    print(f"\nFetched {len(leads)} RemoteOK leads\n")

    for lead in leads:

        print("-" * 60)
        print("Title:", lead["title"])
        print("Author:", lead["author"])
        print("Platform:", lead["platform"])
        print("Published:", lead["published_at"])
        print("URL:", lead["url"])