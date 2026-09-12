import requests
from datetime import datetime
from pipeline.data_validator import LeadDataValidator
from ai.buyer_intent import BuyerIntentEngine
from ai.business_fit import BusinessFitEngine
from pipeline.commercial_ranker import CommercialOpportunityRanker
from pipeline.opportunity_status import (
    determine_opportunity_status,
    freelancer_detail_status

)

from database.db import SessionLocal
from database.models import Lead, Source

from scraper.registry import SCRAPERS
from pipeline.scraper_health import scraper_health
from pipeline.pipeline_logger import get_pipeline_logger
from notifications.notifier import (
    notify_hot_lead,
    notify_pipeline_completed,
    notify_pipeline_failed
)

logger = get_pipeline_logger()

SOURCE_CONFIDENCE = {
    "freelancer": 90,
    "upwork": 90,
    "peopleperhour": 90,
    "guru": 90,
    "remoteok": 70,
    "github": 50,
    "hacker news": 40,
    "dev.to": 40,
    "product hunt": 50,
}


class ProductionLeadPipeline:

    def __init__(self):

        self.scrapers = self.get_enabled_scrapers()
        

        self.buyer_intent_engine = BuyerIntentEngine()

        self.business_fit_engine = BusinessFitEngine()

        self.commercial_ranker = (
            CommercialOpportunityRanker()
        )

        self.validator = LeadDataValidator()

    def get_enabled_scrapers(self):

        db = SessionLocal()

        try:

            enabled_sources = (
                db.query(Source)
                .filter(
                    Source.enabled == True
                )
                .all()
            )

            enabled_names = {
                source.name.strip().lower()
                for source in enabled_sources
            }

            enabled_scrapers = [
                scraper
                for scraper in SCRAPERS
                if scraper.source_name.strip().lower()
                in enabled_names
            ]

            return enabled_scrapers

        finally:

            db.close()

    # ---------------------------------------------------------
    # Timestamp conversion
    # ---------------------------------------------------------

    @staticmethod
    def unix_to_datetime(timestamp):

        if not timestamp:
            return None

        try:
            return datetime.fromtimestamp(
                float(timestamp)
            )

        except (ValueError, TypeError, OSError):
            return None

    # ---------------------------------------------------------
    # Duplicate detection
    # ---------------------------------------------------------

    @staticmethod
    def is_duplicate(db, lead):

        url = lead.get("url", "")

        if url:

            existing = (
                db.query(Lead)
                .filter(Lead.link == url)
                .first()
            )

            if existing:
                return True

        title = lead.get(
            "title",
            ""
        ).strip()

        if not title:
            return True

        existing = (
            db.query(Lead)
            .filter(Lead.title == title)
            .first()
        )

        return existing is not None


    # ---------------------------------------------------------
    # Revalidate existing opportunity
    # ---------------------------------------------------------

    @staticmethod
    def update_existing_opportunity_status(db, lead):
        """
        Revalidate an existing lead using the latest
        source information.

        Only freshness/status fields are updated.
        CRM and business information is preserved.
        """

        url = lead.get("url", "")
        title = lead.get("title", "").strip()

        existing = None

        # Find existing lead by URL first
        if url:
            existing = (
                db.query(Lead)
                .filter(Lead.link == url)
                .first()
            )

        # Fallback to title
        if existing is None and title:
            existing = (
                db.query(Lead)
                .filter(Lead.title == title)
                .first()
            )

        if existing is None:
            return False

        # ---------------------------------------------
        # Always refresh the freshness check timestamp
        # ---------------------------------------------

        existing.freshness_checked_at = lead.get(
            "freshness_checked_at"
        )

        # ---------------------------------------------
        # Only update status when the source provides
        # meaningful status information.
        # ---------------------------------------------

        new_status = lead.get(
            "opportunity_status",
            "UNKNOWN"
        )

        new_source_status = lead.get(
            "source_status",
            ""
        )

        if new_status != "UNKNOWN":
            existing.opportunity_status = new_status

            existing.source_status = (
                new_source_status
            )

        return True

    # ---------------------------------------------------------
    # Freelancer project revalidation
    # ---------------------------------------------------------

    @staticmethod
    def revalidate_freelancer_project(existing):
        """
        Check the current Freelancer status of an existing lead.

        API failures do not change the existing opportunity status.
        """

        project_id = existing.freelancer_project_id

        if not project_id:
            return None

        url = (
            "https://www.freelancer.com/"
            f"api/projects/0.1/projects/{project_id}/"
        )

        try:
            response = requests.get(
                url,
                headers={
                    "User-Agent": "LeadFlow-AI/1.0"
                },
                timeout=20
            )

            if response.status_code == 404:
                return {
                    "opportunity_status": "REMOVED",
                    "source_status": "404"
                }

            response.raise_for_status()

            data = response.json()

            project = (
                data.get("result")
                or {}
            )

            result = freelancer_detail_status(
                project
            )

            if result["opportunity_status"] == "UNKNOWN":
                return None

            return result

        except requests.RequestException as e:

            print(
                f"⚠️ Freelancer revalidation failed "
                f"for project {project_id}: {e}"
            )

            return None

        except Exception as e:

            print(
                f"⚠️ Freelancer revalidation error "
                f"for project {project_id}: {e}"
            )

            return None

    def lead_to_dict(self, lead):
        """
        Normalize scraper Lead objects into the dictionary format
        expected by the production pipeline.
        """

        # Scrapers return Lead dataclass objects.
        # Convert them to a dictionary first.
        if hasattr(lead, "__dict__"):
            lead_data = dict(lead.__dict__)
        elif isinstance(lead, dict):
            lead_data = dict(lead)
        else:
            raise TypeError(f"Unsupported lead type: {type(lead).__name__}")

        raw_data = lead_data.get("raw_data", {}) or {}
        raw_data = dict(raw_data)

        # Preserve Freelancer-specific status/project information.
        if lead_data.get("project_id") is not None:
            raw_data["project_id"] = lead_data.get("project_id")

        if lead_data.get("frontend_project_status") is not None:
            raw_data["frontend_project_status"] = lead_data.get(
                "frontend_project_status"
            )

        if lead_data.get("deleted") is not None:
            raw_data["deleted"] = lead_data.get("deleted")

        platform = lead_data.get(
            "platform",
            lead_data.get("source", "")
        )

        opportunity = determine_opportunity_status(
            platform=platform,
            raw_data=raw_data
        )

        return {
            "title": lead_data.get("title", ""),
            "description": lead_data.get("description", ""),
            "source": lead_data.get("source", platform),
            "url": lead_data.get("url", ""),
            "company": lead_data.get("company", ""),
            "location": lead_data.get("location", ""),
            "budget": lead_data.get("budget", ""),
            "posted_at": lead_data.get("posted_at", ""),
            "contact_name": lead_data.get("contact_name", ""),
            "contact_email": lead_data.get("contact_email", ""),
            "tags": lead_data.get("tags", []),
            "job_names": lead_data.get(
                "job_names",
                lead_data.get("tags", [])
            ),
            "raw_data": raw_data,

            # Opportunity status
            "opportunity_status": opportunity["opportunity_status"],
            "source_status": opportunity["source_status"],
            "freshness_checked_at": opportunity["freshness_checked_at"],

            # Freelancer project ID
            "freelancer_project_id": (
                lead_data.get("project_id")
                or raw_data.get("project_id")
            ),

            # Common pipeline fields
            "platform": platform,
            "matched_keywords": lead_data.get(
                "matched_keywords",
                lead_data.get("tags", [])
            ),
            "urgent": lead_data.get("urgent", False),
            "source_type": lead_data.get(
                "source_type",
                platform
            ),
            "source_confidence": lead_data.get(
                "source_confidence",
                SOURCE_CONFIDENCE.get(
                    str(platform).strip().lower(),
                    50
                )
            ),

            # Commercial fields
            "budget_min": lead_data.get("budget_min"),
            "budget_max": lead_data.get("budget_max"),
            "currency": lead_data.get("currency", ""),
            "project_type": lead_data.get("project_type", ""),
            "bid_count": lead_data.get("bid_count", 0),
            "job_categories": lead_data.get(
                "job_categories",
                []
            ),

            # Raw project ID for compatibility
            "project_id": (
                lead_data.get("project_id")
                or raw_data.get("project_id")
            ),
        }

    # ---------------------------------------------------------
    # Analyze candidate
    # ---------------------------------------------------------

    def analyze_lead(self, lead):

        # Buyer Intent
        buyer_result = (
            self.buyer_intent_engine.analyze(
                lead
            )
        )

        if not buyer_result[
            "is_genuine_opportunity"
        ]:
            return None, {
                "stage": "buyer_intent",
                "score": buyer_result.get(
                    "buyer_intent_score",
                    0
                ),
                "reason": buyer_result.get(
                    "reason",
                    ""
                )
            }

        # Business Fit
        fit_result = (
            self.business_fit_engine.analyze(
                lead
            )
        )

        if not fit_result[
            "is_business_fit"
        ]:
            return None, {
                "stage": "business_fit",
                "score": fit_result.get(
                    "business_fit_score",
                    0
                ),
                "reason": fit_result.get(
                    "reason",
                    ""
                )
            }

        buyer_score = buyer_result[
            "buyer_intent_score"
        ]

        fit_score = fit_result[
            "business_fit_score"
        ]

        # Qualification
        qualification_score = round(
            (buyer_score * 0.60)
            +
            (fit_score * 0.40)
        )

        lead[
            "buyer_intent_score"
        ] = buyer_score

        lead[
            "business_fit_score"
        ] = fit_score

        lead[
            "qualification_score"
        ] = qualification_score

        lead[
            "primary_service"
        ] = fit_result.get(
            "primary_service",
            "unknown"
        )

        # Commercial ranking
        ranking = (
            self.commercial_ranker.calculate(
                lead
            )
        )

        lead.update(ranking)

        return lead, None

    # ---------------------------------------------------------
    # Save lead
    # ---------------------------------------------------------

    def save_lead(self, db, lead):

        record = Lead(

            # Basic information
            title=lead.get(
                "title",
                ""
            ),

            description=lead.get(
                "description",
                ""
            ),

            platform=lead.get(
                "platform",
                ""
            ),

            link=lead.get(
                "url",
                ""
            ),

            # Existing business fields
            business_type="Commercial Opportunity",

            lead_category="Qualified Lead",

            service_needed=lead.get(
                "primary_service",
                ""
            ),

            technology=", ".join(
                lead.get(
                    "matched_keywords",
                    []
                )
            ),

            company_stage="",

            budget=lead.get(
                "budget",
                "Unknown"
            ),

            urgency=(
                "Urgent"
                if lead.get("urgent")
                else "Normal"
            ),

            # Existing scores
            lead_score=lead.get(
                "qualification_score",
                0
            ),

            quality_score=lead.get(
                "business_fit_score",
                0
            ),

            priority_score=lead.get(
                "commercial_score",
                0
            ),

            # Commercial intelligence
            buyer_intent_score=lead.get(
                "buyer_intent_score",
                0
            ),

            business_fit_score=lead.get(
                "business_fit_score",
                0
            ),

            qualification_score=lead.get(
                "qualification_score",
                0
            ),

            commercial_score=lead.get(
                "commercial_score",
                0
            ),

            commercial_priority=lead.get(
                "commercial_priority",
                "LOW"
            ),

            primary_service=lead.get(
                "primary_service",
                ""
            ),

            # Marketplace
            budget_min=str(
                lead.get(
                    "budget_min",
                    ""
                )
            ),

            budget_max=str(
                lead.get(
                    "budget_max",
                    ""
                )
            ),

            currency=lead.get(
                "currency",
                ""
            ),

            project_type=lead.get(
                "project_type",
                ""
            ),

            freelancer_project_id=lead.get(
                "freelancer_project_id"
            ),

            bid_count=lead.get(
                "bid_count",
                0
            ),

            marketplace_urgent=bool(
                lead.get(
                    "urgent",
                    False
                )
            ),

            # Source
            source_type=lead.get(
                "source_type",
                ""
            ),

            source_confidence=lead.get(
                "source_confidence",
                0
            ),

            ranking_reason=lead.get(
                "ranking_reason",
                ""
            ),

            # Timestamps
            submitted_at=self.unix_to_datetime(
                lead.get(
                    "time_submitted"
                )
                or lead.get(
                    "submitdate"
                )
            ),

            updated_at=self.unix_to_datetime(
                lead.get(
                    "time_updated"
                )
            ),

            # -----------------------------------------
            # Opportunity Status
            # -----------------------------------------

            opportunity_status=lead.get(
                "opportunity_status",
                "UNKNOWN"
            ),

            source_status=lead.get(
                "source_status",
                ""
            ),

            freshness_checked_at=lead.get(
                "freshness_checked_at"
            ),

            # -----------------------------------------
            # CRM
            # -----------------------------------------
            
            crm_status="New"

        )

        db.add(record)
        return record


    # ---------------------------------------------------------
    # Run production pipeline
    # ---------------------------------------------------------

    def run(self, limit_per_source=50):

        logger.info("=" * 60)
        logger.info("PRODUCTION LEAD PIPELINE STARTED")
        logger.info("=" * 60)

        db = SessionLocal()

        collected = 0
        buyer_rejected = 0
        fit_rejected = 0
        duplicates = 0
        saved = 0

        print("\n" + "=" * 72)
        print("🚀 LEADFLOW AI — PRODUCTION LEAD PIPELINE")
        print("=" * 72)

        try:

            for scraper in self.scrapers:

                source_name = scraper.source_name

                print(
                    f"\n📡 Source: {source_name}"
                )

                logger.info(
                    f"SCRAPER STARTED: {source_name}"
                )

                scraper_health.start(source_name)

                try:

                    leads = scraper.run()

                    print(
                        f"DEBUG: {source_name} returned "
                        f"{len(leads)} raw leads"
                    )

                    # Validate and clean leads
                    leads = self.validator.validate(leads)

                    print(
                        f"DEBUG: {source_name} has "
                        f"{len(leads)} valid leads after validation"
                    )

                    # Convert validated leads to production dictionaries
                    leads = [
                        self.lead_to_dict(lead)
                        for lead in leads
                    ]

                    print(
                        f"DEBUG: {source_name} converted "
                        f"{len(leads)} leads to dictionaries"
                    )

                    if leads:
                        status_counts = {}

                        for item in leads:
                            status = item.get(
                                "opportunity_status",
                                "UNKNOWN"
                            )

                            status_counts[status] = (
                                status_counts.get(status, 0) + 1
                            )

                        print(
                            f"DEBUG: {source_name} opportunity statuses: "
                            f"{status_counts}"
                        )

                    scraper_health.success(
                        source_name,
                        len(leads)
                    )

                    # Update Source Manager statistics
                    source_record = (
                        db.query(Source)
                        .filter(Source.name == source_name)
                        .first()
                    )

                    if source_record:
                        source_record.leads_collected = len(leads)
                        source_record.status = "Active"

                except Exception as e:

                    scraper_health.failure(
                        source_name,
                        e
                    )

                    logger.exception(
                        f"SCRAPER FAILED: "
                        f"{source_name}: {e}"
                    )

                    print(
                        f"❌ {source_name} failed: {e}"
                    )

                    continue

                collected += len(leads)

                for lead in leads:

                    print(
                        f"DEBUG: Analyzing {source_name}: "
                        f"{lead.get('title', '')[:80]}"
                    )

                    existing_updated = False

                    existing_updated = False

                    if self.is_duplicate(db, lead):

                        # -----------------------------------------------------
                        # Freelancer-specific revalidation
                        # -----------------------------------------------------

                        if source_name.strip().lower() == "freelancer":

                            # Find the existing database record
                            existing = None

                            url = lead.get("url", "")

                            if url:
                                existing = (
                                    db.query(Lead)
                                    .filter(Lead.link == url)
                                    .first()
                                )

                            if existing is None:

                                title = (
                                    lead.get("title", "")
                                    .strip()
                                )

                                if title:
                                    existing = (
                                        db.query(Lead)
                                        .filter(Lead.title == title)
                                        .first()
                                    )

                            # Recheck Freelancer directly
                            if existing is not None:

                                freelancer_result = (
                                    self.revalidate_freelancer_project(
                                        existing
                                    )
                                )

                                if freelancer_result:

                                    lead["opportunity_status"] = (
                                        freelancer_result[
                                            "opportunity_status"
                                        ]
                                    )

                                    lead["source_status"] = (
                                        freelancer_result[
                                            "source_status"
                                        ]
                                    )

                                    lead["freshness_checked_at"] = (
                                        freelancer_result[
                                            "freshness_checked_at"
                                        ]
                                    )

                                    self.update_existing_opportunity_status(
                                        db,
                                        lead
                                    )

                                    print(
                                        "🔄 Freelancer project revalidated:"
                                    )

                                    print(
                                        f"   Status: "
                                        f"{freelancer_result['opportunity_status']}"
                                    )

                                    print(
                                        f"   Source Status: "
                                        f"{freelancer_result['source_status']}"
                                    )

                                else:

                                    # API failure / unknown status:
                                    # preserve the existing database status.
                                    existing.freshness_checked_at = (
                                        lead.get(
                                            "freshness_checked_at"
                                        )
                                    )

                                    print(
                                        "⚠️ Freelancer status could "
                                        "not be confirmed."
                                    )

                                    print(
                                        f"   Existing Status Preserved: "
                                        f"{existing.opportunity_status}"
                                    )

                        else:

                            # -------------------------------------------------
                            # Generic revalidation for other sources
                            # -------------------------------------------------

                            self.update_existing_opportunity_status(
                                db,
                                lead
                            )

                        duplicates += 1

                        print(
                            f"♻️ EXISTING LEAD REVALIDATED: "
                            f"{lead.get('title')}"
                        )

                        continue


                    analyzed, rejection = self.analyze_lead(lead)

                    if (
                        isinstance(rejection, dict)
                        and rejection.get("stage") == "buyer_intent"
                    ):

                        buyer_rejected += 1

                        print(
                            f"❌ BUYER INTENT REJECTED: "
                            f"{lead.get('title')}"
                        )

                        print(
                            f"   Score: {rejection.get('score', 0)}"
                        )

                        print(
                            f"   Reason: {rejection.get('reason', '')}"
                        )

                        continue


                    if (
                        isinstance(rejection, dict)
                        and rejection.get("stage") == "business_fit"
                    ):

                        fit_rejected += 1

                        print(
                            f"❌ BUSINESS FIT REJECTED: "
                            f"{lead.get('title')}"
                        )

                        print(
                            f"   Score: {rejection.get('score', 0)}"
                        )

                        print(
                            f"   Reason: {rejection.get('reason', '')}"
                        )

                        continue


                    if analyzed is None:

                        print(
                            f"❌ ANALYSIS FAILED: "
                            f"{lead.get('title')}"
                        )

                        continue


                    self.save_lead(
                        db,
                        analyzed
                    )

                    saved += 1

                    if analyzed.get("commercial_priority") == "HOT":

                        notify_hot_lead(
                            title=analyzed.get("title", ""),
                            platform=analyzed.get("platform", ""),
                            score=analyzed.get("commercial_score", 0),
                            priority=analyzed.get("commercial_priority", ""),
                            budget=analyzed.get("budget", "Unknown")
                        )

                    print(
                        f"✅ SAVED "
                        f"[{analyzed.get('commercial_priority')}] "
                        f"[{analyzed.get('commercial_score')}] "
                        f"{analyzed.get('title')}"
                    )

            db.commit()

            notify_pipeline_completed(
                collected,
                buyer_rejected,
                fit_rejected,
                duplicates,
                saved
            )

        except Exception as e:

            db.rollback()

            notify_pipeline_failed(e)

            logger.exception(
                f"PRODUCTION PIPELINE FAILED: {e}"
            )

            raise

        finally:

            db.close()

        print("\n" + "=" * 72)
        print("📊 PRODUCTION PIPELINE SUMMARY")
        print("=" * 72)

        print(
            f"📥 Candidates collected  : {collected}"
        )

        print(
            f"❌ Buyer intent rejected : {buyer_rejected}"
        )

        print(
            f"❌ Business fit rejected : {fit_rejected}"
        )

        print(
            f"♻️ Duplicates skipped    : {duplicates}"
        )

        print(
            f"💾 Genuine leads saved   : {saved}"
        )

        print("=" * 72)

        logger.info(
            "PRODUCTION PIPELINE COMPLETED: "
            f"collected={collected}, "
            f"buyer_rejected={buyer_rejected}, "
            f"fit_rejected={fit_rejected}, "
            f"duplicates={duplicates}, "
            f"saved={saved}"
        )

        logger.info("=" * 60)

        return {
            "collected": collected,
            "buyer_intent_rejected": buyer_rejected,
            "business_fit_rejected": fit_rejected,
            "duplicates": duplicates,
            "saved": saved
        }


if __name__ == "__main__":

    pipeline = ProductionLeadPipeline()

    pipeline.run()


    
    