from scraper.github.scraper import GitHubScraper

scraper = GitHubScraper()

leads = scraper.run()

print(f"\nCollected {len(leads)} GitHub leads\n")

for lead in leads[:5]:
    print("-" * 60)
    print("Title:", lead.title)
    print("Author:", lead.contact_name)
    print("Source:", lead.source)
    print("Published:", lead.posted_at)
    print("URL:", lead.url)