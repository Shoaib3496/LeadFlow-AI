from scraper.aggregator import LeadAggregator

from pipeline.data_validator import LeadDataValidator

from pipeline.deduplicator import LeadDeduplicator

from pipeline.ai_pipeline import AIQualificationPipeline


aggregator = LeadAggregator()

leads = aggregator.fetch_all_leads()

validator = LeadDataValidator()

validated = validator.validate(leads)

deduplicator = LeadDeduplicator()

unique = deduplicator.remove_duplicates(
    validated
)

pipeline = AIQualificationPipeline()

qualified = pipeline.qualify(
    unique
)

print("\nSample AI Results\n")

for lead in qualified[:5]:

    print("-" * 60)

    print("Title:", lead.title)

    print("Category:", lead.lead_category)

    print("Business:", lead.business_type)

    print("Technology:", lead.technology)

    print("Urgency:", lead.urgency)

    print("Score:", lead.lead_score)