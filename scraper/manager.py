"""
Production Scraper Manager

Runs all registered scrapers and collects their leads.
"""

from typing import List

from scraper.base.lead_model import Lead
from scraper.registry import SCRAPERS


class ScraperManager:
    """Manages execution of all registered scrapers."""

    def __init__(self):
        self.scrapers = SCRAPERS

    def run_all(self) -> List[Lead]:
        """
        Run all registered scrapers.

        Returns:
            List[Lead]: Combined list of all collected leads.
        """
        all_leads = []

        for scraper in self.scrapers:
            try:
                leads = scraper.run()
                all_leads.extend(leads)
            except Exception as e:
                print(f"Error running {scraper.source_name}: {e}")

        return all_leads

    def run_scraper(self, source_name: str) -> List[Lead]:
        """
        Run a specific scraper by its source name.

        Args:
            source_name (str): Name of the scraper.

        Returns:
            List[Lead]
        """
        for scraper in self.scrapers:
            if scraper.source_name.lower() == source_name.lower():
                return scraper.run()

        raise ValueError(f"Scraper '{source_name}' is not registered.")