from scraper.rss.scraper import RSSScraper

scraper = RSSScraper()

leads = scraper.run()

print(f"\nCollected {len(leads)} leads\n")

for lead in leads[:5]:
    print("-" * 60)
    print("Title:", lead.title)
    print("Source:", lead.source)
    print("Published:", lead.posted_at)
    print("URL:", lead.url)