from db import SessionLocal
from models import Source

db = SessionLocal()

default_sources = [
    {
        "name": "Reddit",
        "category": "Social",
        "country": "Global",
        "enabled": True
    },
    {
        "name": "Product Hunt",
        "category": "Startup",
        "country": "Global",
        "enabled": True
    },
    {
        "name": "Hacker News",
        "category": "Tech",
        "country": "Global",
        "enabled": True
    },
    {
        "name": "Dev.to",
        "category": "Developer",
        "country": "Global",
        "enabled": False
    }
]

for source in default_sources:

    exists = db.query(Source).filter(
        Source.name == source["name"]
    ).first()

    if not exists:

        db.add(Source(**source))

db.commit()

print("Default sources inserted successfully!")