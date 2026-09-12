from scraper.hackernews.scraper import HackerNewsScraper

scraper = HackerNewsScraper()

leads = scraper.run()

print(f"\nCollected {len(leads)} Hacker News leads\n")

for lead in leads[:5]:
    print("-" * 60)
    print("Title:", lead.title)
    print("Author:", lead.contact_name)
    print("Source:", lead.source)
    print("Published:", lead.posted_at)
    print("URL:", lead.url)