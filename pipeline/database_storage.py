from typing import List

from scraper.base.lead_model import Lead as ScrapedLead

from database.db import SessionLocal
from database.models import Lead as DatabaseLead


class LeadDatabaseStorage:
    """
    Step 4.3.3.6

    Stores processed production leads in the LeadFlow AI database.
    """

    def save_all(
        self,
        leads: List[ScrapedLead]
    ):

        db = SessionLocal()

        saved = 0
        duplicates = 0
        errors = 0

        try:

            for lead in leads:

                try:

                    # --------------------------------
                    # Duplicate detection
                    # --------------------------------

                    existing = None

                    if lead.url:

                        existing = (
                            db.query(DatabaseLead)
                            .filter(
                                DatabaseLead.link == lead.url
                            )
                            .first()
                        )

                    # Fallback duplicate check by title
                    if existing is None:

                        existing = (
                            db.query(DatabaseLead)
                            .filter(
                                DatabaseLead.title == lead.title
                            )
                            .first()
                        )

                    if existing:

                        duplicates += 1
                        continue

                    # --------------------------------
                    # Convert scraper lead
                    # into database lead
                    # --------------------------------

                    db_lead = DatabaseLead(

                        title=lead.title,

                        description=lead.description,

                        platform=lead.source,

                        link=lead.url,

                        # AI Qualification

                        business_type=getattr(
                            lead,
                            "business_type",
                            "Unknown"
                        ),

                        lead_category=getattr(
                            lead,
                            "lead_category",
                            "Unknown"
                        ),

                        service_needed=getattr(
                            lead,
                            "service_needed",
                            "Unknown"
                        ),

                        technology=getattr(
                            lead,
                            "technology",
                            "Unknown"
                        ),

                        company_stage=getattr(
                            lead,
                            "company_stage",
                            "Unknown"
                        ),

                        budget=getattr(
                            lead,
                            "budget",
                            "Unknown"
                        ),

                        urgency=getattr(
                            lead,
                            "urgency",
                            "Unknown"
                        ),

                        lead_score=getattr(
                            lead,
                            "lead_score",
                            0
                        ),

                        # Commercial Intelligence

                        buyer_intent_score=getattr(
                            lead,
                            "buyer_intent_score",
                            0
                        ),

                        business_fit_score=getattr(
                            lead,
                            "business_fit_score",
                            0
                        ),

                        qualification_score=getattr(
                            lead,
                            "qualification_score",
                            0
                        ),

                        commercial_score=getattr(
                            lead,
                            "commercial_score",
                            0
                        ),

                        commercial_priority=getattr(
                            lead,
                            "commercial_priority",
                            "LOW"
                        ),

                        primary_service=getattr(
                            lead,
                            "primary_service",
                            "Unknown"
                        ),

                        ranking_reason=getattr(
                            lead,
                            "ranking_reason",
                            ""
                        ),

                        # CRM

                        crm_status="New",

                        assigned_to="Founder"
                    )

                    db.add(db_lead)

                    saved += 1

                except Exception as e:

                    errors += 1

                    print(
                        f"[DATABASE ERROR] "
                        f"{lead.title}: {e}"
                    )

            # Commit everything
            db.commit()

        except Exception as e:

            db.rollback()

            print(
                "\nDatabase transaction failed:",
                e
            )

            raise

        finally:

            db.close()

        print("\n" + "=" * 60)
        print("DATABASE STORAGE SUMMARY")
        print("=" * 60)

        print(f"Input Leads          : {len(leads)}")
        print(f"New Leads Saved      : {saved}")
        print(f"Duplicates Skipped   : {duplicates}")
        print(f"Errors               : {errors}")

        return {
            "input": len(leads),
            "saved": saved,
            "duplicates": duplicates,
            "errors": errors
        }