from database.db import SessionLocal
from database.models import Lead


class DatabaseWriter:

    def __init__(self):
        self.db = SessionLocal()

    def save(self, lead):

        # ------------------------------------
        # Check if lead already exists
        # ------------------------------------
        existing = self.db.query(Lead).filter(
            Lead.title == lead.get("title"),
            Lead.platform == lead.get("platform")
        ).first()

        if existing:
            print(f"Duplicate skipped: {lead.get('title')}")
            return

        # ------------------------------------
        # Create new Lead object
        # ------------------------------------
        db_lead = Lead(

            title=lead.get("title"),
            description=lead.get("description"),
            platform=lead.get("platform"),
            link=lead.get("url"),

            company_name=lead.get("company_name"),
            industry=lead.get("industry"),
            website=lead.get("website"),
            email=lead.get("email"),
            linkedin=lead.get("linkedin"),
            twitter=lead.get("twitter"),
            country=lead.get("country"),

            business_type=lead.get("business_type"),
            lead_category=lead.get("lead_category"),
            service_needed=lead.get("service_needed"),
            technology=lead.get("technology"),
            company_stage=lead.get("company_stage"),

            budget=lead.get("budget"),
            urgency=lead.get("urgency"),
            lead_score=lead.get("lead_score"),

            crm_status="New"
        )

        self.db.add(db_lead)
        self.db.commit()

        print(f"Saved: {lead.get('title')}")

    def close(self):
        self.db.close()