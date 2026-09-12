import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from database.models import Lead
from ai.lead_filter import is_qualified_lead

post = "Need website for my restaurant business"

if is_qualified_lead(post):

    db = SessionLocal()

    new_lead = Lead(
        title=post,
        description=post,
        platform="Manual Test",
        score=0,
        budget="Unknown"
    )

    db.add(new_lead)
    db.commit()

    print("Qualified lead saved!")

else:
    print("Not a qualified lead")