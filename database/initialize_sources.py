from database.db import SessionLocal
from database.models import Source


SOURCES = [
    {
        "name": "RSS",
        "category": "Technology",
        "country": "Global",
    },
    {
        "name": "GitHub",
        "category": "Technology",
        "country": "Global",
    },
    {
        "name": "Hacker News",
        "category": "Technology",
        "country": "Global",
    },
    {
        "name": "Dev.to",
        "category": "Technology",
        "country": "Global",
    },
    {
        "name": "RemoteOK",
        "category": "Jobs",
        "country": "Global",
    },
    {
        "name": "Product Hunt",
        "category": "Technology",
        "country": "Global",
    },
]


def initialize_sources():

    db = SessionLocal()

    try:

        created = 0
        existing = 0

        for source_data in SOURCES:

            source = (
                db.query(Source)
                .filter(
                    Source.name == source_data["name"]
                )
                .first()
            )

            if source:
                existing += 1
                continue

            source = Source(
                name=source_data["name"],
                category=source_data["category"],
                country=source_data["country"],
                enabled=True,
                status="Active",
                last_run=None,
                leads_collected=0,
            )

            db.add(source)

            created += 1

        db.commit()

        print("=" * 60)
        print("SOURCE INITIALIZATION")
        print("=" * 60)
        print(f"Created : {created}")
        print(f"Existing: {existing}")
        print(f"Total   : {created + existing}")
        print("=" * 60)

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    initialize_sources()