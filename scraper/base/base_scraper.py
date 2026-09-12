from abc import ABC, abstractmethod
from typing import List
import logging

from scraper.base.lead_model import Lead


class BaseScraper(ABC):
    """
    Abstract base class for all production scrapers.

    Every scraper must inherit from this class and implement
    the scrape() method.
    """

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(source_name)

    @abstractmethod
    def scrape(self) -> List[Lead]:
        """
        Collect leads from the source.

        Returns:
            List[Lead]
        """
        pass

    def run(self) -> List[Lead]:
        """
        Execute the scraper with common logging and
        exception handling.
        """

        self.logger.info(f"Starting {self.source_name} scraper...")

        try:

            leads = self.scrape()

            self.logger.info(
                f"{self.source_name}: {len(leads)} leads collected."
            )

            return leads

        except Exception as e:

            self.logger.exception(
                f"{self.source_name} scraper failed: {e}"
            )

            return []