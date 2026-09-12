from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Lead:
    """
    Standard Lead Model used by every production scraper.
    """

    title: str
    description: str

    source: str
    url: str

    company: Optional[str] = None

    location: Optional[str] = None

    budget: Optional[str] = None

    posted_at: Optional[str] = None

    contact_name: Optional[str] = None

    contact_email: Optional[str] = None

    tags: List[str] = field(default_factory=list)

    raw_data: dict = field(default_factory=dict)