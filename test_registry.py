from scraper.registry import SCRAPERS

print("Registered Scrapers")

for scraper in SCRAPERS:
    print(scraper.source_name)