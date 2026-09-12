from scraper.base.base_scraper import BaseScraper
from scraper.base.lead_model import Lead


class DummyScraper(BaseScraper):

    def __init__(self):
        super().__init__("Dummy")

    def scrape(self):

        return [

            Lead(
                title="Test Lead",
                description="Testing",
                source="Dummy",
                url="https://example.com"
            )

        ]


scraper = DummyScraper()

results = scraper.run()

print(results)