import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from scraper.aggregator import LeadAggregator

from ai.lead_scoring import calculate_score
from ai.opportunity_detector import OpportunityDetector
from ai.buyer_intent import BuyerIntentEngine

from pipeline.priority_engine import PriorityEngine

from database.db import SessionLocal
from database.models import Lead

from notifications.notifier import notify_new_lead


# ============================================================
# SAVE LEAD
# ============================================================

def save_lead(db, lead_data):

    # --------------------------------------------------------
    # Check duplicate
    # --------------------------------------------------------

    existing = db.query(Lead).filter(
        Lead.title == lead_data.get("title"),
        Lead.platform == lead_data.get("platform")
    ).first()

    if existing:

        print(
            f"Skipped Duplicate: "
            f"{lead_data.get('title')}"
        )

        return False

    # --------------------------------------------------------
    # Create database object
    # --------------------------------------------------------

    lead = Lead(

        # Basic
        title=lead_data.get("title", ""),
        description=lead_data.get("description", ""),
        platform=lead_data.get("platform", ""),
        link=lead_data.get("url", ""),

        # Company / enrichment fields
        company_name=lead_data.get(
            "company_name",
            "Unknown"
        ),

        industry=lead_data.get(
            "industry",
            "Unknown"
        ),

        website=lead_data.get(
            "website",
            "Unknown"
        ),

        email=lead_data.get(
            "email",
            "Unknown"
        ),

        linkedin=lead_data.get(
            "linkedin",
            "Unknown"
        ),

        twitter=lead_data.get(
            "twitter",
            "Unknown"
        ),

        country=lead_data.get(
            "country",
            "Unknown"
        ),

        # AI Analysis
        business_type=lead_data.get(
            "business_type",
            "Unknown"
        ),

        lead_category=lead_data.get(
            "lead_category",
            "Unknown"
        ),

        service_needed=lead_data.get(
            "service_needed",
            "Unknown"
        ),

        technology=lead_data.get(
            "technology",
            "Unknown"
        ),

        company_stage=lead_data.get(
            "company_stage",
            "Unknown"
        ),

        # Business
        budget=lead_data.get(
            "budget",
            "Unknown"
        ),

        urgency=lead_data.get(
            "urgency",
            "Unknown"
        ),

        # Scores
        lead_score=lead_data.get(
            "lead_score",
            0
        ),

        quality_score=lead_data.get(
            "quality_score",
            0
        ),

        priority_score=lead_data.get(
            "priority_score",
            0
        ),

        # Opportunity
        opportunity=lead_data.get(
            "opportunity",
            ""
        ),

        reason=lead_data.get(
            "reason",
            ""
        ),

        outreach_strategy=lead_data.get(
            "outreach_strategy",
            ""
        ),

        # CRM
        status="New"
    )

    db.add(lead)

    # --------------------------------------------------------
    # Notification
    # --------------------------------------------------------

    notify_new_lead(
        lead.title,
        lead.priority_score
    )

    return True


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():

    db = SessionLocal()

    # --------------------------------------------------------
    # Initialize Engines
    # --------------------------------------------------------

    aggregator = LeadAggregator()

    buyer_intent_engine = BuyerIntentEngine()

    detector = OpportunityDetector()

    priority_engine = PriorityEngine()

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    raw_candidates = 0

    buyer_rejected = 0

    genuine_opportunities = 0

    saved = 0

    duplicates = 0

    try:

        # ====================================================
        # STEP 1 — COLLECT LIVE CANDIDATES
        # ====================================================

        print("\n" + "=" * 70)
        print("🚀 LeadFlow AI Genuine Lead Pipeline")
        print("=" * 70)

        print("\n📡 Collecting candidates from live sources...\n")

        leads = aggregator.fetch_all_leads()

        raw_candidates = len(leads)

        print(
            f"\n📥 Candidates after aggregation: "
            f"{raw_candidates}"
        )

        # ====================================================
        # STEP 2 — PROCESS EACH CANDIDATE
        # ====================================================

        print("\n🧠 Running Buyer Intent Detection...\n")

        for lead in leads:

            title = lead.get(
                "title",
                "Untitled Lead"
            )

            # ------------------------------------------------
            # BUYER INTENT
            # ------------------------------------------------

            intent_result = (
                buyer_intent_engine.analyze(lead)
            )

            lead["buyer_intent_score"] = (
                intent_result[
                    "buyer_intent_score"
                ]
            )

            lead["intent_level"] = (
                intent_result[
                    "intent_level"
                ]
            )

            # ------------------------------------------------
            # Reject candidates without genuine intent
            # ------------------------------------------------

            if not intent_result[
                "is_genuine_opportunity"
            ]:

                buyer_rejected += 1

                print(
                    f"❌ REJECTED "
                    f"[Intent "
                    f"{lead['buyer_intent_score']}] "
                    f"{title}"
                )

                continue

            # ------------------------------------------------
            # Genuine opportunity
            # ------------------------------------------------

            genuine_opportunities += 1

            print("\n" + "-" * 70)

            print(
                f"✅ GENUINE OPPORTUNITY "
                f"[Intent "
                f"{lead['buyer_intent_score']}]"
            )

            print(
                f"Title    : {title}"
            )

            print(
                f"Platform : "
                f"{lead.get('platform', 'Unknown')}"
            )

            print(
                f"Intent   : "
                f"{lead.get('intent_level')}"
            )

            print(
                f"Reason   : "
                f"{intent_result.get('reason')}"
            )

            # ------------------------------------------------
            # EXISTING LEAD SCORE
            # ------------------------------------------------

            text = (
                lead.get("title", "")
                + " "
                + lead.get(
                    "description",
                    ""
                )
            )

            lead["lead_score"] = (
                calculate_score(text)
            )

            # ------------------------------------------------
            # OPPORTUNITY DETECTION
            # ------------------------------------------------

            insight = detector.detect(
                lead
            )

            lead.update(insight)

            # ------------------------------------------------
            # PRIORITY SCORE
            # ------------------------------------------------

            lead["priority_score"] = (
                priority_engine.calculate_priority(
                    lead
                )
            )

            print(
                f"Priority : "
                f"{lead['priority_score']}"
            )

            print(
                f"Opportunity: "
                f"{lead.get('opportunity', 'Unknown')}"
            )

            # ------------------------------------------------
            # DATABASE
            # ------------------------------------------------

            if save_lead(
                db,
                lead
            ):

                saved += 1

            else:

                duplicates += 1

        # ====================================================
        # COMMIT
        # ====================================================

        db.commit()

        # ====================================================
        # FINAL SUMMARY
        # ====================================================

        print("\n")
        print("=" * 70)
        print("📊 GENUINE LEAD PIPELINE SUMMARY")
        print("=" * 70)

        print(
            f"📥 Candidates Collected      : "
            f"{raw_candidates}"
        )

        print(
            f"❌ Buyer Intent Rejected     : "
            f"{buyer_rejected}"
        )

        print(
            f"✅ Genuine Opportunities     : "
            f"{genuine_opportunities}"
        )

        print(
            f"💾 New Leads Saved           : "
            f"{saved}"
        )

        print(
            f"♻️ Duplicates Skipped        : "
            f"{duplicates}"
        )

        if raw_candidates > 0:

            acceptance_rate = (
                genuine_opportunities
                / raw_candidates
            ) * 100

        else:

            acceptance_rate = 0

        print(
            f"🎯 Genuine Lead Rate         : "
            f"{acceptance_rate:.2f}%"
        )

        print("=" * 70)

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        db.rollback()

        print("\n❌ PIPELINE ERROR")
        print(f"Reason: {e}")

        raise

    # ========================================================
    # ALWAYS CLOSE DATABASE
    # ========================================================

    finally:

        db.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()