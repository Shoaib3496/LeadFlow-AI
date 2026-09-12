import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from database.models import Lead

db = SessionLocal()

new_lead = Lead(
    title="Need Website for Restaurant",
    description="Looking for a developer to build a restaurant website.",
    platform="Reddit",
    score=0,
    budget="Unknown"
)

db.add(new_lead)
db.commit()

print("Lead added successfully!")