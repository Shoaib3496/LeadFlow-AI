import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.hackernews_connector import fetch_hackernews_posts
from connectors.producthunt_connector import fetch_producthunt_posts
from connectors.reddit_connector import fetch_reddit_posts
from connectors.devto_connector import fetch_devto_posts


BUSINESS_SOURCES = [
    {
        "name": "Hacker News",
        "enabled": True,
        "function": fetch_hackernews_posts
    },
    {
        "name": "Product Hunt",
        "enabled": True,
        "function": fetch_producthunt_posts
    },
    {
        "name": "Dev.to",
        "enabled": True,
        "function": fetch_devto_posts
    },
    {
        "name": "Reddit",
        "enabled": False,   # Enable when API is available
        "function": fetch_reddit_posts
    }
]


def collect_business_sources():

    all_leads = []

    for source in BUSINESS_SOURCES:

        if not source["enabled"]:
            continue

        print(f"\nCollecting from {source['name']}...")

        try:

            posts = source["function"]()

            print(f"{len(posts)} posts collected")

            all_leads.extend(posts)

        except Exception as e:

            print(f"{source['name']} Error: {e}")

    return all_leads


if __name__ == "__main__":

    posts = collect_business_sources()

    print(f"\nTotal Posts: {len(posts)}")