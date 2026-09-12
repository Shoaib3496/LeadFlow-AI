from datetime import datetime

from database.db import SessionLocal
from database.models import Lead
from pipeline.production_pipeline import ProductionLeadPipeline


def test_opportunity_status_revalidation():
    db = SessionLocal()

    test_url = "https://example.com/temp-revalidation-test"

    lead = Lead(
        title="TEMP REVALIDATION TEST",
        description="Temporary test lead",
        crm_status="New",
        link=test_url,
        opportunity_status="UNKNOWN",
        source_status="",
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    lead_id = lead.id

    try:
        print("\n=== OPPORTUNITY REVALIDATION TEST ===")
        print(f"Temporary lead ID: {lead_id}")

        # ---------------------------------------------------------
        # TEST 1: UNKNOWN -> OPEN
        # ---------------------------------------------------------
        result = ProductionLeadPipeline.update_existing_opportunity_status(
            db,
            {
                "url": test_url,
                "title": "TEMP REVALIDATION TEST",
                "opportunity_status": "OPEN",
                "source_status": "open",
                "freshness_checked_at": datetime.now(),
            },
        )

        db.flush()
        db.refresh(lead)

        print(
            "UNKNOWN -> OPEN:",
            result,
            lead.opportunity_status,
            lead.source_status,
        )

        assert result is True
        assert lead.opportunity_status == "OPEN"
        assert lead.source_status == "open"
        assert lead.freshness_checked_at is not None

        print("✓ UNKNOWN -> OPEN passed")

        # ---------------------------------------------------------
        # TEST 2: OPEN -> CLOSED
        # ---------------------------------------------------------
        result = ProductionLeadPipeline.update_existing_opportunity_status(
            db,
            {
                "url": test_url,
                "title": "TEMP REVALIDATION TEST",
                "opportunity_status": "CLOSED",
                "source_status": "closed",
                "freshness_checked_at": datetime.now(),
            },
        )

        db.flush()
        db.refresh(lead)

        print(
            "OPEN -> CLOSED:",
            result,
            lead.opportunity_status,
            lead.source_status,
        )

        assert result is True
        assert lead.opportunity_status == "CLOSED"
        assert lead.source_status == "closed"

        print("✓ OPEN -> CLOSED passed")

        # ---------------------------------------------------------
        # TEST 3: CLOSED -> REMOVED
        # ---------------------------------------------------------
        result = ProductionLeadPipeline.update_existing_opportunity_status(
            db,
            {
                "url": test_url,
                "title": "TEMP REVALIDATION TEST",
                "opportunity_status": "REMOVED",
                "source_status": "deleted",
                "freshness_checked_at": datetime.now(),
            },
        )

        db.flush()
        db.refresh(lead)

        print(
            "CLOSED -> REMOVED:",
            result,
            lead.opportunity_status,
            lead.source_status,
        )

        assert result is True
        assert lead.opportunity_status == "REMOVED"
        assert lead.source_status == "deleted"

        print("✓ CLOSED -> REMOVED passed")

        print("=== REVALIDATION TEST PASSED ===")

    finally:
        test_lead = (
            db.query(Lead)
            .filter(Lead.id == lead_id)
            .first()
        )

        if test_lead:
            db.delete(test_lead)
            db.commit()

        db.close()

        print("✓ Temporary test lead removed")