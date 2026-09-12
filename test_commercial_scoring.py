from scraper.aggregator import LeadAggregator

from pipeline.data_validator import LeadDataValidator
from pipeline.deduplicator import LeadDeduplicator
from pipeline.ai_pipeline import AIQualificationPipeline
from pipeline.commercial_scoring import CommercialScoringEngine


# ---------------------------------------
# 1. Collect
# ---------------------------------------

aggregator = LeadAggregator()

leads = aggregator.fetch_all_leads()


# ---------------------------------------
# 2. Validate
# ---------------------------------------

validator = LeadDataValidator()

leads = validator.validate(leads)


# ---------------------------------------
# 3. Deduplicate
# ---------------------------------------

deduplicator = LeadDeduplicator()

leads = deduplicator.remove_duplicates(leads)


# ---------------------------------------
# 4. AI Qualification
# ---------------------------------------

ai_pipeline = AIQualificationPipeline()

leads = ai_pipeline.qualify(leads)


# ---------------------------------------
# 5. Commercial Scoring
# ---------------------------------------

scoring_engine = CommercialScoringEngine()

leads = scoring_engine.score_all(leads)


# ---------------------------------------
# Display highest-value opportunities
# ---------------------------------------

print("\n" + "=" * 60)
print("TOP COMMERCIAL OPPORTUNITIES")
print("=" * 60)

for lead in leads[:10]:

    print("\n" + "-" * 60)

    print("Title:", lead.title)

    print("Source:", lead.source)

    print(
        "Commercial Score:",
        lead.commercial_score
    )

    print(
        "Priority:",
        lead.commercial_priority
    )

    print(
        "Buyer Intent:",
        lead.buyer_intent_score
    )

    print(
        "Business Fit:",
        lead.business_fit_score
    )

    print(
        "Qualification:",
        lead.qualification_score
    )

    print(
        "Service:",
        lead.primary_service
    )

    print(
        "AI Lead Score:",
        lead.lead_score
    )

    print(
        "Reason:",
        lead.ranking_reason
    )

    print(
        "URL:",
        lead.url
    )