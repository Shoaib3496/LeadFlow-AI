import sys
import os
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from database.models import Lead

db = SessionLocal()

leads = db.query(Lead).all()

with open("leads_export.csv", "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow([
        "ID",
        "Title",
        "Platform",
        "Business Type",
        "Budget",
        "Urgency",
        "Lead Score"
    ])

    for lead in leads:

        writer.writerow([
            lead.id,
            lead.title,
            lead.platform,
            lead.business_type,
            lead.budget,
            lead.urgency,
            lead.lead_score
        ])

print("CSV Export Completed!")
print("File: leads_export.csv")