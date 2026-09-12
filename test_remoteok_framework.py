from scraper.remoteok.scraper import RemoteOKScraper

scraper = RemoteOKScraper()

leads = scraper.run()

print(f"\nCollected {len(leads)} RemoteOK leads\n")

for lead in leads[:5]:
    print("-" * 60)
    print("Title:", lead.title)
    print("Company:", lead.company)
    print("Source:", lead.source)
    print("Published:", lead.posted_at)
    print("URL:", lead.url)