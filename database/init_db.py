from db import engine, SessionLocal
from models import Base, Source

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Seed default sources only if the table is empty
if db.query(Source).count() == 0:

    sources = [
        Source(
            name="Hacker News",
            category="Tech",
            country="Global",
            enabled=True,
            status="Active",
            leads_collected=0
        ),
        Source(
            name="Dev.to",
            category="Tech",
            country="Global",
            enabled=True,
            status="Active",
            leads_collected=0
        ),
        Source(
            name="Product Hunt",
            category="Startup",
            country="Global",
            enabled=True,
            status="Active",
            leads_collected=0
        ),
        Source(
            name="Reddit",
            category="Social",
            country="Global",
            enabled=False,
            status="Inactive",
            leads_collected=0
        )
    ]

    db.add_all(sources)
    db.commit()

db.close()

print("Database created and default sources added successfully!")