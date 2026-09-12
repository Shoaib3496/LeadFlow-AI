import time

from scraper.aggregator import LeadAggregator

from pipeline.data_validator import LeadDataValidator
from pipeline.deduplicator import LeadDeduplicator
from pipeline.ai_pipeline import AIQualificationPipeline
from pipeline.commercial_scoring import CommercialScoringEngine
from pipeline.database_storage import LeadDatabaseStorage
from pipeline.pipeline_logger import get_pipeline_logger


# ==========================================
# LOGGER
# ==========================================

logger = get_pipeline_logger()


def run_pipeline():

    start_time = time.time()

    logger.info("=" * 60)
    logger.info("LEADFLOW AI PRODUCTION PIPELINE STARTED")
    logger.info("=" * 60)

    try:

        # ==========================================
        # STEP 1 — Production Collection
        # ==========================================

        logger.info("STEP 1: Production lead collection started")

        aggregator = LeadAggregator()

        leads = aggregator.fetch_all_leads()

        logger.info(
            f"STEP 1 COMPLETE: {len(leads)} leads collected"
        )


        # ==========================================
        # STEP 2 — Validation
        # ==========================================

        logger.info("STEP 2: Data validation started")

        validator = LeadDataValidator()

        leads = validator.validate(leads)

        logger.info(
            f"STEP 2 COMPLETE: {len(leads)} valid leads"
        )


        # ==========================================
        # STEP 3 — Deduplication
        # ==========================================

        logger.info("STEP 3: Deduplication started")

        before_deduplication = len(leads)

        deduplicator = LeadDeduplicator()

        leads = deduplicator.remove_duplicates(leads)

        duplicates_removed = (
            before_deduplication - len(leads)
        )

        logger.info(
            "STEP 3 COMPLETE: "
            f"{duplicates_removed} duplicates removed, "
            f"{len(leads)} unique leads remaining"
        )


        # ==========================================
        # STEP 4 — AI Qualification
        # ==========================================

        logger.info("STEP 4: AI qualification started")

        ai_pipeline = AIQualificationPipeline()

        leads = ai_pipeline.qualify(leads)

        qualified_count = sum(
            1
            for lead in leads
            if getattr(
                lead,
                "lead_category",
                "Unknown"
            ) != "Unknown"
        )

        logger.info(
            "STEP 4 COMPLETE: "
            f"{len(leads)} leads processed, "
            f"{qualified_count} categorized"
        )


        # ==========================================
        # STEP 5 — Commercial Scoring
        # ==========================================

        logger.info("STEP 5: Commercial scoring started")

        scoring = CommercialScoringEngine()

        leads = scoring.score_all(leads)

        hot_count = sum(
            1 for lead in leads
            if getattr(
                lead,
                "commercial_priority",
                ""
            ) == "HOT"
        )

        warm_count = sum(
            1 for lead in leads
            if getattr(
                lead,
                "commercial_priority",
                ""
            ) == "WARM"
        )

        medium_count = sum(
            1 for lead in leads
            if getattr(
                lead,
                "commercial_priority",
                ""
            ) == "MEDIUM"
        )

        low_count = sum(
            1 for lead in leads
            if getattr(
                lead,
                "commercial_priority",
                ""
            ) == "LOW"
        )

        actionable_count = sum(
            1 for lead in leads
            if getattr(
                lead,
                "commercial_score",
                0
            ) >= 40
        )

        logger.info(
            "STEP 5 COMPLETE: "
            f"HOT={hot_count}, "
            f"WARM={warm_count}, "
            f"MEDIUM={medium_count}, "
            f"LOW={low_count}"
        )

        logger.info(
            f"Actionable commercial opportunities: "
            f"{actionable_count}"
        )


        # ==========================================
        # STEP 6 — Database Storage
        # ==========================================

        logger.info("STEP 6: Database storage started")

        storage = LeadDatabaseStorage()

        storage.save_all(leads)

        logger.info(
            f"STEP 6 COMPLETE: "
            f"{len(leads)} leads passed to database storage"
        )


        # ==========================================
        # PIPELINE COMPLETE
        # ==========================================

        duration = time.time() - start_time

        logger.info("=" * 60)
        logger.info(
            "LEADFLOW AI PRODUCTION PIPELINE COMPLETED"
        )
        logger.info(
            f"Final processed leads: {len(leads)}"
        )
        logger.info(
            f"Actionable opportunities: {actionable_count}"
        )
        logger.info(
            f"Pipeline duration: {duration:.2f} seconds"
        )
        logger.info("=" * 60)

        print("\n" + "=" * 60)
        print("PRODUCTION PIPELINE COMPLETED")
        print("=" * 60)
        print(f"Processed Leads          : {len(leads)}")
        print(f"Actionable Opportunities : {actionable_count}")
        print(f"Duration                 : {duration:.2f} seconds")
        print("=" * 60)


    except Exception as e:

        duration = time.time() - start_time

        logger.exception(
            f"PIPELINE FAILED after "
            f"{duration:.2f} seconds: {e}"
        )

        print("\n" + "=" * 60)
        print("PRODUCTION PIPELINE FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print("Check the pipeline log for details.")
        print("=" * 60)

        raise


if __name__ == "__main__":

    run_pipeline()