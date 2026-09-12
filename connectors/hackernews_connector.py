import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from config.settings import HN_LIMIT


TOP_STORIES_API = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_API = "https://hacker-news.firebaseio.com/v0/item/{}.json"

# Number of stories to scan
MAX_SCAN = 100


# Keywords that may indicate startup/business opportunities
BUSINESS_KEYWORDS = [
    "startup",
    "saas",
    "show hn",
    "launch",
    "founder",
    "business",
    "website",
    "shopify",
    "ecommerce",
    "ai",
    "automation",
    "developer",
    "agency",
    "app",
    "mobile",
    "customer",
    "client",
    "product",
    "service",
    "software",
    "crm",
    "marketing",
    "sales",
    "analytics",
    "dashboard",
]


def is_relevant(title):
    """
    Returns True if the title contains
    startup/business related keywords.
    """

    if not title:
        return False

    title = title.lower()

    return any(keyword in title for keyword in BUSINESS_KEYWORDS)


def fetch_hackernews_posts():
    """
    Fetch relevant Hacker News stories
    using the official Hacker News API.
    """

    posts = []

    try:

        response = requests.get(
            TOP_STORIES_API,
            timeout=10
        )

        response.raise_for_status()

        story_ids = response.json()

        scanned = 0

        for story_id in story_ids:

            if scanned >= MAX_SCAN:
                break

            scanned += 1

            try:

                story = requests.get(
                    ITEM_API.format(story_id),
                    timeout=10
                ).json()

            except Exception:
                continue

            if not story:
                continue

            title = story.get("title", "")

            if not is_relevant(title):
                continue

            post = {
                "title": title,
                "link": story.get(
                    "url",
                    f"https://news.ycombinator.com/item?id={story_id}"
                ),
                "source": "Hacker News",
                "type": "discussion"
            }

            posts.append(post)

            # Stop after collecting enough relevant stories
            if len(posts) >= HN_LIMIT:
                break

    except Exception as e:
        print(f"Hacker News Error: {e}")

    return posts


if __name__ == "__main__":

    print("=" * 60)
    print("LeadFlow AI - Hacker News Connector")
    print("=" * 60)

    posts = fetch_hackernews_posts()

    print(f"\nRelevant Posts Collected: {len(posts)}\n")

    for i, post in enumerate(posts, start=1):

        print(f"{i}. {post['title']}")
        print(f"   {post['link']}")
        print()