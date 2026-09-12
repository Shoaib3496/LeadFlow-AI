from scraper.aggregator import LeadAggregator
from pipeline.data_validator import LeadDataValidator
from pipeline.deduplicator import LeadDeduplicator


aggregator = LeadAggregator()

leads = aggregator.fetch_all_leads()

validator = LeadDataValidator()

validated = validator.validate(leads)

deduplicator = LeadDeduplicator()

unique = deduplicator.remove_duplicates(
    validated
)

print("\nSample Unique Leads\n")

for lead in unique[:5]:

    print("-" * 60)

    print("Title:", lead.title)

    print("Source:", lead.source)

    print("URL:", lead.url)