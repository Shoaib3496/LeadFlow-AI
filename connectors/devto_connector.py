import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

DEVTO_API = "https://dev.to/api/articles"


def fetch_devto_posts():

    posts = []

    try:

        response = requests.get(
            DEVTO_API,
            timeout=15
        )

        response.raise_for_status()

        articles = response.json()

        for article in articles[:20]:

            post = {

                "title": article.get("title", ""),

                "description": article.get(
                    "description",
                    ""
                ),

                "link": article.get(
                    "url",
                    ""
                ),

                "source": "Dev.to",

                "type": "discussion"

            }

            posts.append(post)

    except Exception as e:

        print(f"Dev.to Error: {e}")

    return posts


if __name__ == "__main__":

    posts = fetch_devto_posts()

    print(f"\nCollected {len(posts)} Dev.to posts\n")

    for post in posts:

        print("=" * 60)

        print("Title :", post["title"])

        print("Link  :", post["link"])