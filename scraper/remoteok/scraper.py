import requests
from typing import List

from scraper.base.base_scraper import BaseScraper
from scraper.base.lead_model import Lead
from config.tech_keywords import TECH_KEYWORDS


REMOTEOK_API = "https://remoteok.com/api"


class RemoteOKScraper(BaseScraper):

    def __init__(self):
        super().__init__("RemoteOK")

    def scrape(self) -> List[Lead]:

        leads = []

        scanned = 0
        skipped = 0

        headers = {
            "User-Agent": "LeadFlow-AI"
        }

        response = requests.get(
            REMOTEOK_API,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        jobs = response.json()

        # First element contains API metadata
        jobs = jobs[1:]

        # ---------------------------------------------------------
        # Strong technical-role signals
        # ---------------------------------------------------------
        technical_role_keywords = [
            "software engineer",
            "software developer",
            "backend developer",
            "backend engineer",
            "frontend developer",
            "frontend engineer",
            "full stack developer",
            "full-stack developer",
            "fullstack developer",
            "full stack engineer",
            "full-stack engineer",
            "web developer",
            "web engineer",
            "mobile developer",
            "mobile engineer",
            "ios developer",
            "android developer",
            "python developer",
            "python engineer",
            "java developer",
            "java engineer",
            "javascript developer",
            "typescript developer",
            "react developer",
            "node developer",
            "node.js developer",
            "devops engineer",
            "cloud engineer",
            "data engineer",
            "data scientist",
            "machine learning engineer",
            "ml engineer",
            "ai engineer",
            "artificial intelligence engineer",
            "llm engineer",
            "generative ai engineer",
            "prompt engineer",
            "automation engineer",
            "qa engineer",
            "test automation engineer",
            "security engineer",
            "cybersecurity engineer",
            "site reliability engineer",
            "sre",
            "solutions engineer",
            "software architect",
            "technical architect",
        
        ]

        # ---------------------------------------------------------
        # Explicitly reject non-technical job categories
        # ---------------------------------------------------------
        excluded_role_keywords = [
            "retail",
            "store manager",
            "assistant store",
            "mail carrier",
            "customer service",
            "customer support",
            "sales representative",
            "sales manager",
            "account executive",
            "account manager",
            "recruiter",
            "recruiting",
            "human resources",
            "hr manager",
            "marketing manager",
            "content writer",
            "copywriter",
            "social media",
            "virtual assistant",
            "administrative assistant",
            "operations manager",
            "restaurant",
            "hospitality",
            "driver",
            "delivery",
            "nurse",
            "healthcare",
            "teacher",
            "legal",
            "finance manager",
            "financial advisor"
        ]

        for job in jobs:

            scanned += 1

            title = job.get("position", "") or ""
            description = job.get("description", "") or ""
            tags = job.get("tags", []) or []

            title_lower = title.lower().strip()
            description_lower = description.lower()

            tag_text = " ".join(
                str(tag).lower()
                for tag in tags
            )

            # -----------------------------------------------------
            # 1. Reject clearly non-technical roles by TITLE
            # -----------------------------------------------------
            if any(
                keyword in title_lower
                for keyword in excluded_role_keywords
            ):
                skipped += 1
                continue

            # -----------------------------------------------------
            # 2. Require an actual technical role in the TITLE
            # -----------------------------------------------------
            has_technical_title = any(
                keyword in title_lower
                for keyword in technical_role_keywords
            )

            if not has_technical_title:
                skipped += 1
                continue

            # -----------------------------------------------------
            # 3. Require at least one technical technology signal
            # -----------------------------------------------------
            combined = (
                f"{title_lower} "
                f"{description_lower} "
                f"{tag_text}"
            )

            has_technology_signal = any(
                keyword.lower() in combined
                for keyword in TECH_KEYWORDS
            )

            if not has_technology_signal:
                skipped += 1
                continue

            # -----------------------------------------------------
            # 4. Create standardized Lead
            # -----------------------------------------------------
            leads.append(
                Lead(
                    title=title,
                    description=description[:1000],
                    source="RemoteOK",
                    url=job.get("url", ""),
                    company=job.get("company", ""),
                    posted_at=job.get("date", ""),
                    contact_name=job.get("company", ""),
                    tags=tags,
                    raw_data=job
                )
            )

            if len(leads) >= 20:
                break

        print("RemoteOKScraper:")
        print(f"  Jobs Scanned         : {scanned}")
        print(f"  Irrelevant Skipped   : {skipped}")
        print(f"  Business Leads Found : {len(leads)}")

        return leads