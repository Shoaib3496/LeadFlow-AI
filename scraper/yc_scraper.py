import requests

from scraper.base_scraper import BaseScraper
from config.tech_keywords import TECH_KEYWORDS


YC_API = "https://www.ycombinator.com/api/companies"


class YCScraper(BaseScraper):

    def fetch_leads(self, limit=20):

        leads = []
        scanned = 0
        skipped = 0

        headers = {
            "User-Agent": "LeadFlow-AI"
        }

        params = {
            "batch": "",
            "company_size": "",
            "isHiring": "true"
        }

        try:

            response = requests.get(
                YC_API,
                headers=headers,
                params=params,
                timeout=20
            )

            response.raise_for_status()

            companies = response.json().get("companies", [])

            for company in companies:

                scanned += 1

                name = company.get("name", "")
                tagline = company.get("one_liner", "") or ""
                description = company.get("long_description", "") or ""

                combined = f"{tagline} {description}".lower()

                if not any(keyword in combined for keyword in TECH_KEYWORDS):
                    skipped += 1
                    continue

                leads.append(

                    self.normalize_lead(

                        title=name,

                        description=f"{tagline}\n\n{description[:1000]}",

                        url=company.get("website", ""),

                        platform="YCombinator",

                        author=name,

                        published_at=""

                    )

                )

                if len(leads) >= limit:
                    break

            print("YCScraper:")
            print(f"  Companies Scanned    : {scanned}")
            print(f"  Irrelevant Skipped   : {skipped}")
            print(f"  Business Leads Found : {len(leads)}")

            return leads

        except Exception as e:

            print(f"[YCScraper] Error: {e}")
            return []


if __name__ == "__main__":

    scraper = YCScraper()

    leads = scraper.fetch_leads()

    print(f"\nFetched {len(leads)} YC leads\n")

    for lead in leads:

        print("-" * 60)
        print("Company:", lead["title"])
        print("Platform:", lead["platform"])
        print("Website:", lead["url"])