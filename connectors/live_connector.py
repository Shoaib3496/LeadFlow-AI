import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connectors.reddit_connector import fetch_reddit_posts
from connectors.hackernews_connector import fetch_hackernews_posts
from connectors.producthunt_connector import fetch_producthunt_posts


def fetch_live_sources():
    """
    Collect leads from all available connectors.
    If one connector fails, the others continue to work.
    """

    all_leads = []

    connectors = [
        ("Reddit", fetch_reddit_posts),
        ("Hacker News", fetch_hackernews_posts),
        ("Product Hunt", fetch_producthunt_posts),
    ]

    for name, connector in connectors:

        try:
            print(f"\nCollecting from {name} Connector...")

            leads = connector()

            if leads:
                print(f"{name}: {len(leads)} leads collected")
                all_leads.extend(leads)
            else:
                print(f"{name}: No leads found")

        except Exception as e:
            print(f"{name} Connector Error: {e}")

    print(f"\nTotal Leads Collected: {len(all_leads)}")

    return all_leads


if __name__ == "__main__":

    print("=" * 50)
    print("LeadFlow AI - Live Connector")
    print("=" * 50)

    leads = fetch_live_sources()

    print("\nCollected Leads:\n")

    for lead in leads:
        print(lead)