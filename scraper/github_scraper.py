import requests

from scraper.base_scraper import BaseScraper
from config.tech_keywords import TECH_KEYWORDS


GITHUB_SEARCH_API = "https://api.github.com/search/issues"


class GitHubScraper(BaseScraper):

    def fetch_leads(self, limit=20):

        leads = []
        scanned = 0
        skipped = 0

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "LeadFlow-AI"
        }

        # Search using a few high-value keywords
        search_queries = [
            "website",
            "api",
            "automation",
            "dashboard",
            "crm",
            "saas",
            "bug",
            "feature"
        ]

        try:

            for keyword in search_queries:

                params = {
                    "q": (
                        f"{keyword} "
                        "is:issue "
                        "state:open "
                        "comments:>1 "
                    ),
                    "sort": "updated",
                    "order": "desc",
                    "per_page": 10
                }

                for _ in range(3):
                    try:
                        response = requests.get(GITHUB_SEARCH_API, headers=headers, params=params, timeout=15)
                        response.raise_for_status()
                        break
                    except requests.RequestException:
                        continue
                

                response.raise_for_status()

                data = response.json()

                for issue in data.get("items", []):

                    scanned += 1

                    title = issue.get("title", "")
                    description = issue.get("body", "") or ""

                    combined = f"{title} {description}".lower()

                    if not any(
                        keyword in combined
                        for keyword in TECH_KEYWORDS
                    ):
                        skipped += 1
                        continue

                    leads.append(

                        self.normalize_lead(

                            title=title,

                            description=description[:1000],

                            url=issue.get("html_url", ""),

                            platform="GitHub",

                            author=issue.get("user", {}).get("login", ""),

                            published_at=issue.get("created_at", "")

                        )

                    )

                    if len(leads) >= limit:
                        break

                if len(leads) >= limit:
                    break

            # Remove duplicates

            unique = []
            seen = set()

            for lead in leads:

                if lead["url"] not in seen:
                    seen.add(lead["url"])
                    unique.append(lead)

            print("GitHubScraper:")
            print(f"  Issues Scanned       : {scanned}")
            print(f"  Irrelevant Skipped   : {skipped}")
            print(f"  Business Leads Found : {len(unique)}")

            return unique

        except Exception as e:

            print(f"[GitHubScraper] Error: {e}")

            return []


if __name__ == "__main__":

    scraper = GitHubScraper()

    leads = scraper.fetch_leads()

    print(f"\nFetched {len(leads)} GitHub leads\n")

    for lead in leads:

        print("-" * 60)
        print("Title:", lead["title"])
        print("Author:", lead["author"])
        print("Platform:", lead["platform"])
        print("Published:", lead["published_at"])
        print("URL:", lead["url"])