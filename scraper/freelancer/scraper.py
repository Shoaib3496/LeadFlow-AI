from typing import List

from scraper.base.base_scraper import BaseScraper
from scraper.base.lead_model import Lead
from scraper.freelancer_scraper import FreelancerScraper as LegacyFreelancerScraper


class FreelancerProductionScraper(BaseScraper):

    def __init__(self):
        super().__init__("Freelancer")
        self.freelancer = LegacyFreelancerScraper()

    def scrape(self) -> List[Lead]:

        raw_leads = self.freelancer.fetch_leads(
            limit=20
        )

        leads = []

        for item in raw_leads:

            leads.append(
                Lead(
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    source="Freelancer",
                    url=item.get("url", ""),
                    company=item.get("company"),
                    location=item.get("location"),
                    budget=item.get("budget"),
                    posted_at=item.get("published_at"),
                    contact_name=item.get("author"),
                    contact_email=item.get("contact_email"),
                    tags=item.get("matched_keywords", []),
                    raw_data=item
                )
            )

        print(
            f"FreelancerProductionScraper: "
            f"{len(leads)} production leads"
        )

        return leads