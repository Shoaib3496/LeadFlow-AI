import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from database.models import Lead

db = SessionLocal()

leads = db.query(Lead).all()

seen_titles = set()
deleted = 0

for lead in leads:

    if lead.title in seen_titles:
        db.delete(lead)
        deleted += 1

    else:
        seen_titles.add(lead.title)

db.commit()

print(f"Removed {deleted} duplicate leads")