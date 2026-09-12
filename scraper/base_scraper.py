from abc import ABC, abstractmethod
from typing import List, Dict


class BaseScraper(ABC):
    """
    Base class for all lead scrapers.
    Every scraper must return a list of leads
    in the same standardized format.
    """

    @abstractmethod
    def fetch_leads(self) -> List[Dict]:
        """
        Fetch leads from the source.

        Returns:
            [
                {
                    "title": "...",
                    "description": "...",
                    "url": "...",
                    "platform": "...",
                    "author": "...",
                    "published_at": "..."
                }
            ]
        """
        pass

    @staticmethod
    def normalize_lead(
        title: str,
        description: str,
        url: str,
        platform: str,
        author: str = "",
        published_at: str = ""
    ) -> Dict:

        return {
            "title": title.strip(),
            "description": description.strip(),
            "url": url.strip(),
            "platform": platform.strip(),
            "author": author.strip(),
            "published_at": published_at.strip(),
        }