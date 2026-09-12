from datetime import datetime

from database.db import SessionLocal
from database.models import Source

from scraper.manager import ScraperManager
from pipeline.process_leads import LeadProcessingPipeline


def run_enabled_scrapers():

    db = SessionLocal()

    try:

        enabled_sources = (
            db.query(Source)
            .filter(Source.enabled == True)
            .all()
        )

        scraper_manager = ScraperManager()
        pipeline = LeadProcessingPipeline()

        total_leads = 0

        for source in enabled_sources:

            try:

                # -----------------------------------------
                # Mark source as running
                # -----------------------------------------

                source.status = "Running"
                db.commit()

                print(
                    f"\n📡 Running source: {source.name}"
                )

                # -----------------------------------------
                # Run the ACTUAL registered scraper
                # -----------------------------------------

                raw_leads = (
                    scraper_manager.run_scraper(
                        source.name
                    )
                )

                print(
                    f"📥 {source.name} collected "
                    f"{len(raw_leads)} leads"
                )

                # -----------------------------------------
                # Send those leads through existing
                # AI + enrichment + database pipeline
                # -----------------------------------------

                processed_leads = (
                    pipeline.process(
                        raw_leads=raw_leads
                    )
                )

                lead_count = len(processed_leads)

                total_leads += lead_count

                # -----------------------------------------
                # Update source monitoring
                # -----------------------------------------

                source.status = "Active"

                source.last_run = datetime.now()

                source.leads_collected += lead_count

                db.commit()

                print(
                    f"✅ {source.name} completed "
                    f"→ {lead_count} processed"
                )

            except Exception as e:

                source.status = "Failed"

                db.commit()

                print(
                    f"❌ Error while processing "
                    f"{source.name}: {e}"
                )

        return {
            "status": "success",
            "qualified_leads": total_leads,
            "message": (
                "Enabled source collection "
                "completed successfully."
            )
        }

    finally:

        db.close()