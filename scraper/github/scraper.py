import requests
from typing import List

from scraper.base.base_scraper import BaseScraper
from scraper.base.lead_model import Lead
from config.tech_keywords import TECH_KEYWORDS


GITHUB_SEARCH_API = "https://api.github.com/search/issues"


class GitHubScraper(BaseScraper):

    def __init__(self):
        super().__init__("GitHub")

    def scrape(self) -> List[Lead]:

        leads = []
        scanned = 0
        skipped = 0

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "LeadFlow-AI"
        }

        search_queries = [
            "website",
            "api",
            "automation",
            "dashboard",
            "crm",
            "saas",
            "feature"
        ]

        direct_request_keywords = [
            "need a developer",
            "need developer",
            "looking for developer",
            "looking for a developer",
            "hire developer",
            "hiring developer",
            "need someone to build",
            "need someone to develop",
            "looking for someone to build",
            "looking for someone to develop",
            "looking for freelancer",
            "need a freelancer",
            "hire freelancer",
            "can someone build",
            "can someone develop",
            "seeking developer",
            "seeking a developer",
        ]

        project_keywords = [
            "build",
            "develop",
            "development",
            "integration",
            "implementation",
            "automation",
            "website",
            "web app",
            "mobile app",
            "application",
            "dashboard",
            "api",
            "saas",
            "crm",
            "ecommerce",
        ]

        need_language = [
            "need",
            "looking for",
            "seeking",
            "want to",
            "would like",
            "help with",
            "help me",
            "someone to"
        ]

        excluded_keywords = [
            "documentation",
            "docs",
            "research paper",
            "review paper",
            "literature review",
            "tutorial",
            "benchmark",
            "changelog",
            "release notes",
            "dependency update",
            "dependencies",
            "ci/cd",
            "github actions",
            "unit test",
            "test coverage",
            "refactor",
            "refactoring",
            "lint",
            "formatting",
            "typo",
            "translation",
            "localization",
            "security advisory",
            "vulnerability report",
            "rfc",
            "flagged",
            "version",
            "versions",
            "stuck on",
            "cannot receive",
            "regression",
            "regressions",
            "broken",
            "not working",
            "doesn't work",
            "does not work",
            "error",
            "crash",
            "crashes",
            "fix",
            "fixes",
            "fixing",

            # Open-source maintenance
            "maintainer",
            "upstream",
            "pull request",
            "open source",

            # Bounty / reward
            "bug bounty",
            "bounty",
            "reward",
            "paid issue"
        ]

        for keyword in search_queries:

            params = {
                "q": (
                    f"{keyword} "
                    "is:issue "
                    "state:open "
                    "comments:>1"
                ),
                "sort": "updated",
                "order": "desc",
                "per_page": 10
            }

            response = None

            for _ in range(3):
                try:
                    response = requests.get(
                        GITHUB_SEARCH_API,
                        headers=headers,
                        params=params,
                        timeout=15
                    )
                    response.raise_for_status()
                    break
                except requests.RequestException:
                    continue

            if response is None:
                continue

            data = response.json()

            for issue in data.get("items", []):

                scanned += 1

                title = issue.get("title", "")
                description = issue.get("body", "") or ""

                combined = f"{title} {description}".lower()

                # -----------------------------------------
                # Reject bot accounts
                # -----------------------------------------

                username = (
                    issue.get("user", {})
                    .get("login", "")
                    .lower()
                )

                if (
                    username.endswith("[bot]")
                    or username.endswith("-bot")
                ):
                    skipped += 1
                    continue

                # -----------------------------------------
                # Technology relevance
                # -----------------------------------------

                if not any(
                    tech in combined
                    for tech in TECH_KEYWORDS
                ):
                    skipped += 1
                    continue

                # -----------------------------------------
                # Reject obvious open-source noise
                # -----------------------------------------

                if any(
                    keyword in combined
                    for keyword in excluded_keywords
                ):
                    skipped += 1
                    continue

                # -----------------------------------------
                # Commercial/project intent
                # -----------------------------------------

                has_direct_request = any(
                    keyword in combined
                    for keyword in direct_request_keywords
                )

                has_project_signal = any(
                    keyword in combined
                    for keyword in project_keywords
                )

                has_need_language = any(
                    keyword in combined
                    for keyword in [
                        "need",
                        "looking for",
                        "seeking",
                        "want to",
                        "would like",
                        "help with",
                        "help me",
                        "someone to",
                    ]
                )

                if not has_direct_request and not (
                    has_project_signal
                    and has_need_language
                ):
                    skipped += 1
                    continue

                

                leads.append(
                    Lead(
                        title=title,
                        description=description[:1000],
                        source="GitHub",
                        url=issue.get("html_url", ""),
                        posted_at=issue.get("created_at", ""),
                        contact_name=issue.get("user", {}).get("login", ""),
                        raw_data=issue
                    )
                )

                if len(leads) >= 20:
                    break

            if len(leads) >= 20:
                break

        # Remove duplicate URLs
        unique = []
        seen = set()

        for lead in leads:
            if lead.url not in seen:
                seen.add(lead.url)
                unique.append(lead)

        print("GitHubScraper:")
        print(f"  Issues Scanned       : {scanned}")
        print(f"  Irrelevant Skipped   : {skipped}")
        print(f"  Business Leads Found : {len(unique)}")

        return unique