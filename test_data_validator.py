from scraper.aggregator import LeadAggregator
from pipeline.data_validator import LeadDataValidator


aggregator = LeadAggregator()

leads = aggregator.fetch_all_leads()

validator = LeadDataValidator()

validated = validator.validate(leads)

print("\nSample Valid Leads\n")

for lead in validated[:5]:

    print("-" * 60)
    print("Title:", lead.title)
    print("Source:", lead.source)
    print("URL:", lead.url)