from scraper.rss.scraper import RSSScraper
from scraper.github.scraper import GitHubScraper
from scraper.hackernews.scraper import HackerNewsScraper
from scraper.devto.scraper import DevToScraper
from scraper.remoteok.scraper import RemoteOKScraper
from scraper.producthunt.scraper import ProductHuntScraper
from scraper.freelancer.scraper import FreelancerProductionScraper

SCRAPERS = [
    RSSScraper(),
    GitHubScraper(),
    HackerNewsScraper(),
    DevToScraper(),
    RemoteOKScraper(),
    ProductHuntScraper(),
    FreelancerProductionScraper(),
]