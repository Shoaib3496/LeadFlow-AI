import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from database.models import Lead

db = SessionLocal()

# Sort leads by highest score first
leads = db.query(Lead)\
          .order_by(Lead.lead_score.desc())\
          .all()

print("\n========== LEAD RANKINGS ==========\n")

for lead in leads:
    print(
        f"""
ID: {lead.id}
Title: {lead.title}
Business Type: {lead.business_type}
Budget: {lead.budget}
Urgency: {lead.urgency}
Lead Score: {lead.lead_score}
Platform: {lead.platform}
-----------------------------------
"""
    )

print(f"\nTotal Leads: {len(leads)}")