from dataclasses import asdict
from scraper.aggregator import LeadAggregator

from ai.business_lead_classifier import classify_business_lead
from ai.analyzer import analyze_lead

from pipeline.rule_filter import should_process
from pipeline.enricher import enrich_lead
from pipeline.database_writer import DatabaseWriter
import time
from datetime import datetime


class LeadProcessingPipeline:

    def __init__(self):
        self.aggregator = LeadAggregator()

    @staticmethod
    def normalize_lead(lead):

        if isinstance(lead, dict):
            return lead

        return asdict(lead)

    def process(self, raw_leads=None):

        start_time = time.time()

        print("\n" + "=" * 70)
        print("🚀 LeadFlow AI Pipeline Started")
        print("Started At :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 70)

        print("\n📥 Collecting live leads...\n")

        if raw_leads is None:
            raw_leads = self.aggregator.fetch_all_leads()
        else:
            print(
                f"Using supplied scraper leads : {len(raw_leads)}"
            )

        raw_leads = [
            self.normalize_lead(lead)
            for lead in raw_leads
        ]

        print(f"✅ Raw Leads Collected : {len(raw_leads)}")

        writer = DatabaseWriter()

        # -----------------------------
        # Rule-Based Filtering
        # -----------------------------
        filtered_leads = []

        for lead in raw_leads:

            if should_process(lead):
                filtered_leads.append(lead)

        removed_by_rules = len(raw_leads) - len(filtered_leads)

        print(f"🛡 Rule Filter Passed : {len(filtered_leads)}")
        print(f"❌ Removed by Rules  : {removed_by_rules}")

        qualified = []
        rejected = 0

        # -----------------------------
        # AI Processing
        # -----------------------------
        print("\n🤖 Running AI Analysis...\n")

        for lead in filtered_leads:

            text = (
                lead.get("title", "")
                + "\n\n"
                + lead.get("description", "")
            )

            print("\n" + "=" * 80)
            print("TITLE:")
            print(lead.get("title", ""))

            print("\nDESCRIPTION:")
            print(lead.get("description", ""))

            # -----------------------------------------
            # AI Business Lead Classification
            # -----------------------------------------

            result = classify_business_lead(text)

            print("\nCLASSIFIER RESULT:")
            print(result)
            print("=" * 80)

            # -----------------------------------------
            # Reject non-business leads
            # -----------------------------------------

            if not result.get("is_business_lead", False):

                rejected += 1

                print(
                    f"🚫 AI REJECTED: "
                    f"{lead.get('title', '')}"
                )

                continue

            # -----------------------------------------
            # AI Lead Analysis
            # -----------------------------------------

            analysis = analyze_lead(text)

            if analysis:
                lead.update(analysis)

            # -----------------------------------------
            # Lead Enrichment
            # -----------------------------------------

            lead = enrich_lead(lead)

            # -----------------------------------------
            # Database Storage
            # -----------------------------------------

            writer.save(lead)

            qualified.append(lead)

        writer.close()

        elapsed = round(time.time() - start_time, 2)

        print("\n" + "=" * 70)
        print("✅ Pipeline Completed Successfully")
        print("=" * 70)

        print(f"📥 Raw Leads          : {len(raw_leads)}")
        print(f"🛡 Passed Rule Filter : {len(filtered_leads)}")
        print(f"🤖 AI Qualified       : {len(qualified)}")
        print(f"🚫 AI Rejected        : {rejected}")
        print(f"⏱ Total Time         : {elapsed} sec")

        print("=" * 70)

        return qualified

if __name__ == "__main__":

    pipeline = LeadProcessingPipeline()

    leads = pipeline.process()

    print("\nSample Leads\n")

    for lead in leads[:5]:

        print("-" * 60)
        print("Title      :", lead.get("title"))
        print("Platform   :", lead.get("platform"))
        print("Category   :", lead.get("lead_category"))
        print("Technology :", lead.get("technology"))
        print("Urgency    :", lead.get("urgency"))
        print("Score      :", lead.get("lead_score"))