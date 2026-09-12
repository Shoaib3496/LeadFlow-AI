from scraper.manager import ScraperManager


class LeadAggregator:
    """
    Step 4.3.3.1
    Collects leads from every registered production scraper.
    No validation, deduplication or AI processing is performed here.
    """

    def __init__(self):
        self.manager = ScraperManager()

    def fetch_all_leads(self):

        leads = self.manager.run_all()

        print("\n" + "=" * 60)
        print("LEAD AGGREGATION SUMMARY")
        print("=" * 60)

        print(f"Total Leads Collected : {len(leads)}")

        return leads


if __name__ == "__main__":

    aggregator = LeadAggregator()

    leads = aggregator.fetch_all_leads()

    print("\nSample Leads\n")

    for lead in leads[:5]:

        print("-" * 60)
        print("Title:", lead.title)
        print("Source:", lead.source)
        print("URL:", lead.url)