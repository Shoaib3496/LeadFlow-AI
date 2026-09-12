from fastapi.testclient import TestClient

from backend.api import app
from database.db import SessionLocal
from database.models import Lead


client = TestClient(app)


def test_closed_opportunity_protection():
    db = SessionLocal()

    lead = Lead(
        title="TEMP CLOSED OPPORTUNITY TEST",
        description="Temporary test lead",
        crm_status="New",
        opportunity_status="CLOSED",
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    lead_id = lead.id

    try:
        print("\n=== CLOSED OPPORTUNITY PROTECTION TEST ===")
        print(f"Temporary lead ID: {lead_id}")

        # Test 1: AI outreach must be blocked
        response = client.post(
            f"/lead/{lead_id}/generate-outreach"
        )

        print(
            "Generate outreach:",
            response.status_code,
            response.json()
        )

        assert response.status_code == 409
        assert "CLOSED" in response.json()["detail"]

        print("✓ Generate outreach blocked")

        # Test 2: Contacted status must be blocked
        response = client.post(
            f"/lead/{lead_id}/status",
            data={"crm_status": "Contacted"}
        )

        print(
            "Mark contacted:",
            response.status_code,
            response.json()
        )

        assert response.status_code == 409
        assert "CLOSED" in response.json()["detail"]

        print("✓ Contact action blocked")

    finally:
        # Always remove the temporary test lead
        db.delete(lead)
        db.commit()
        db.close()

    print("✓ Temporary test lead removed")
    print("=== TEST PASSED ===")