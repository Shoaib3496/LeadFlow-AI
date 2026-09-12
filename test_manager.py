from scraper.manager import ScraperManager

manager = ScraperManager()

print("Registered Scrapers:")

for scraper in manager.scrapers:
    print("-", scraper.source_name)

leads = manager.run_all()

print(f"\nTotal Leads Collected: {len(leads)}")