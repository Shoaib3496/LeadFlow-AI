from scraper.producthunt.scraper import ProductHuntScraper

scraper = ProductHuntScraper()

leads = scraper.run()

print(f"\nCollected {len(leads)} Product Hunt leads\n")

for lead in leads[:5]:
    print("-" * 60)
    print("Title:", lead.title)
    print("Author:", lead.contact_name)
    print("Source:", lead.source)
    print("Published:", lead.posted_at)
    print("URL:", lead.url)