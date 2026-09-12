from dataclasses import dataclass


@dataclass
class LeadItem:
    title: str
    link: str
    source: str
    type: str