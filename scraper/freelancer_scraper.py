import requests
from datetime import datetime, timezone

from scraper.base_scraper import BaseScraper


FREELANCER_PROJECTS_API = (
    "https://www.freelancer.com/api/projects/0.1/projects/active/"
)


class FreelancerScraper(BaseScraper):

    def __init__(self):

        # ----------------------------------------------------
        # Services LeadFlow is interested in selling
        # ----------------------------------------------------

        self.keywords = [

            # Web Development
            "website",
            "web development",
            "web developer",
            "web application",
            "web app",
            "landing page",

            # CMS / Ecommerce
            "wordpress",
            "shopify",
            "woocommerce",
            "ecommerce",
            "e-commerce",

            # Frontend
            "react",
            "next.js",
            "vue",
            "angular",

            # Backend
            "python",
            "django",
            "flask",
            "fastapi",
            "node.js",
            "laravel",
            "php",

            # Mobile
            "mobile app",
            "android",
            "ios",
            "flutter",
            "react native",

            # Software
            "software development",
            "custom software",
            "saas",

            # API / Automation
            "api integration",
            "api",
            "automation",

            # AI
            "ai chatbot",
            "chatbot",
            "artificial intelligence",
            "machine learning",
            "ai automation",

            # Data
            "dashboard",
            "data analytics",
            "data analysis",

            # Business software
            "crm",
            "erp"
        ]

        # ----------------------------------------------------
        # Obvious non-development/service categories
        # ----------------------------------------------------

        self.negative_job_categories = {
            "Writing & Content",
            "Sales & Marketing",
            "Translation & Languages",
        }

    # ========================================================
    # FETCH
    # ========================================================

    def fetch_leads(self, limit=20):

        leads = []

        scanned = 0
        irrelevant = 0

        try:

            params = {

                # Scan more projects so that filtering has
                # enough candidates to work with.
                "limit": 100,

                "compact": "true",

                "job_details": "true",

                "sort_field": "time_updated",
            }

            headers = {
                "User-Agent": "LeadFlow-AI/1.0"
            }

            response = requests.get(

                FREELANCER_PROJECTS_API,

                params=params,

                headers=headers,

                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            projects = (
                data
                .get("result", {})
                .get("projects", [])
            )

            # =================================================
            # PROCESS PROJECTS
            # =================================================

            for project in projects:

                scanned += 1

                # ---------------------------------------------
                # Basic project validation
                # ---------------------------------------------

                if project.get("deleted"):
                    irrelevant += 1
                    continue

                if project.get("nonpublic"):
                    irrelevant += 1
                    continue

                status = project.get(
                    "frontend_project_status",
                    ""
                )

                if status and status.lower() != "open":
                    irrelevant += 1
                    continue

                # ---------------------------------------------
                # Title
                # ---------------------------------------------

                title = (
                    project.get("title", "")
                    or ""
                ).strip()

                # ---------------------------------------------
                # Description
                #
                # Freelancer active-project endpoint provides
                # preview_description.
                # ---------------------------------------------

                description = (
                    project.get(
                        "preview_description",
                        ""
                    )
                    or ""
                ).strip()

                # ---------------------------------------------
                # Freelancer job/category information
                # ---------------------------------------------

                jobs = (
                    project.get("jobs", [])
                    or []
                )

                job_names = []

                job_categories = []

                for job in jobs:

                    name = (
                        job.get("name", "")
                        or ""
                    )

                    if name:
                        job_names.append(name)

                    category = (
                        job.get(
                            "category",
                            {}
                        )
                        or {}
                    )

                    category_name = (
                        category.get(
                            "name",
                            ""
                        )
                        or ""
                    )

                    if category_name:
                        job_categories.append(
                            category_name
                        )

                # ---------------------------------------------
                # Search text
                # ---------------------------------------------

                combined_text = " ".join([

                    title,

                    description,

                    " ".join(job_names)

                ]).lower()

                # ---------------------------------------------
                # Relevant software keywords
                # ---------------------------------------------

                matched_keywords = [

                    keyword

                    for keyword in self.keywords

                    if keyword in combined_text
                ]

                if not matched_keywords:

                    irrelevant += 1
                    continue

                # ---------------------------------------------
                # Prevent obvious category false positives
                #
                # We don't automatically reject a project just
                # because one category is marketing/writing if
                # it also contains a real software category.
                # ---------------------------------------------

                software_categories = {

                    "Websites, IT & Software",
                    "Mobile Phones & Computing",
                    "Design, Media & Architecture",
                    "Data Entry & Admin",
                }

                has_software_category = any(

                    category in software_categories

                    for category in job_categories
                )

                only_negative_categories = (

                    bool(job_categories)

                    and all(

                        category
                        in self.negative_job_categories

                        for category in job_categories
                    )
                )

                if (
                    only_negative_categories
                    and not has_software_category
                ):

                    irrelevant += 1
                    continue

                # ---------------------------------------------
                # Project URL
                # ---------------------------------------------

                seo_url = (
                    project.get("seo_url", "")
                    or ""
                )

                if seo_url:

                    url = (
                        "https://www.freelancer.com"
                        f"/projects/{seo_url}"
                    )

                else:

                    project_id = project.get(
                        "id",
                        ""
                    )

                    url = (
                        "https://www.freelancer.com"
                        f"/projects/{project_id}"
                    )

                # ---------------------------------------------
                # Budget
                # ---------------------------------------------

                budget = (
                    project.get("budget", {})
                    or {}
                )

                minimum = budget.get(
                    "minimum"
                )

                maximum = budget.get(
                    "maximum"
                )

                currency_data = (
                    project.get(
                        "currency",
                        {}
                    )
                    or {}
                )

                currency = (
                    currency_data.get(
                        "code",
                        ""
                    )
                    or ""
                )

                if (
                    minimum is not None
                    and maximum is not None
                ):

                    budget_text = (

                        f"{minimum} - "
                        f"{maximum} "
                        f"{currency}"

                    )

                elif minimum is not None:

                    budget_text = (
                        f"From {minimum} {currency}"
                    )

                elif maximum is not None:

                    budget_text = (
                        f"Up to {maximum} {currency}"
                    )

                else:

                    budget_text = "Unknown"

                # ---------------------------------------------
                # Published time
                # ---------------------------------------------

                submit_timestamp = (
                    project.get("submitdate")
                )

                published_at = ""

                if submit_timestamp:

                    try:

                        published_at = (
                            datetime
                            .fromtimestamp(
                                submit_timestamp,
                                tz=timezone.utc
                            )
                            .isoformat()
                        )

                    except Exception:

                        published_at = str(
                            submit_timestamp
                        )

                # ---------------------------------------------
                # Project metadata
                # ---------------------------------------------

                project_type = (
                    project.get(
                        "type",
                        "Unknown"
                    )
                    or "Unknown"
                )

                urgent = bool(
                    project.get(
                        "urgent",
                        False
                    )
                )

                bid_stats = (
                    project.get(
                        "bid_stats",
                        {}
                    )
                    or {}
                )

                bid_count = (
                    bid_stats.get(
                        "bid_count",
                        0
                    )
                    or 0
                )

                # ---------------------------------------------
                # Normalize into LeadFlow format
                # ---------------------------------------------

                lead = self.normalize_lead(

                    title=title,

                    description=description,

                    url=url,

                    platform="Freelancer",

                    author=str(
                        project.get(
                            "owner_id",
                            ""
                        )
                    ),

                    published_at=published_at
                )


                # ---------------------------------------------
                # Budget Information
                # ---------------------------------------------

                lead["budget"] = budget_text

                lead["budget_min"] = minimum

                lead["budget_max"] = maximum

                lead["currency"] = currency


                # ---------------------------------------------
                # Marketplace Information
                # ---------------------------------------------

                lead["project_type"] = project_type

                lead["urgent"] = urgent

                lead["bid_count"] = bid_count

                # ---------------------------------------------
                # Opportunity Status Information
                # ---------------------------------------------

                lead["frontend_project_status"] = status
                lead["deleted"] = bool(project.get("deleted"))
                lead["project_id"] = project.get("id")


                # ---------------------------------------------
                # Timestamp / Freshness Information
                # ---------------------------------------------

                lead["submitdate"] = project.get(
                    "submitdate"
                )

                lead["time_submitted"] = project.get(
                    "time_submitted"
                )

                lead["time_updated"] = project.get(
                    "time_updated"
                )


                # ---------------------------------------------
                # Source Information
                # ---------------------------------------------

                lead["source_type"] = (
                    "Direct Opportunity"
                )

                lead["source_confidence"] = 95


                # ---------------------------------------------
                # Skill / Service Information
                # ---------------------------------------------

                lead["matched_keywords"] = (
                    matched_keywords
                )

                lead["job_names"] = (
                    job_names
                )

                lead["job_categories"] = (
                    job_categories
                )

                # ---------------------------------------------
                # Source confidence
                #
                # This is a posted Freelancer project rather
                # than a general article/news item.
                # ---------------------------------------------

                lead["source_confidence"] = 90

                leads.append(lead)

                if len(leads) >= limit:
                    break

            # =================================================
            # SUMMARY
            # =================================================

            print("\nFreelancerScraper:")

            print(
                f"  Projects Scanned     : "
                f"{scanned}"
            )

            print(
                f"  Irrelevant Skipped   : "
                f"{irrelevant}"
            )

            print(
                f"  Opportunities Found  : "
                f"{len(leads)}"
            )

            return leads

        # ====================================================
        # ERRORS
        # ====================================================

        except requests.RequestException as e:

            print(
                "Freelancer HTTP Error:",
                e
            )

            return []

        except Exception as e:

            print(
                "Freelancer Error:",
                e
            )

            return []


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    scraper = FreelancerScraper()

    leads = scraper.fetch_leads(
        limit=10
    )

    print(
        f"\nFetched "
        f"{len(leads)} "
        f"Freelancer opportunities\n"
    )

    for lead in leads:

        print("=" * 70)

        print(
            "Title:",
            lead.get("title")
        )

        print(
            "Platform:",
            lead.get("platform")
        )

        print(
            "Budget:",
            lead.get("budget")
        )

        print(
            "Type:",
            lead.get("project_type")
        )

        print(
            "Urgent:",
            lead.get("urgent")
        )

        print(
            "Bids:",
            lead.get("bid_count")
        )

        print(
            "Jobs:",
            lead.get("job_names")
        )

        print(
            "Categories:",
            lead.get(
                "job_categories"
            )
        )

        print(
            "Keywords:",
            lead.get(
                "matched_keywords"
            )
        )

        print(
            "URL:",
            lead.get("url")
        )

        description = (
            lead.get(
                "description",
                ""
            )
        )

        print(
            "Description:",
            description[:500]
        )

        print()