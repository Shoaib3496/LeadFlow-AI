import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from connectors.producthunt_auth import get_access_token


GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"


QUERY = """
{
  posts(first: 20) {
    edges {
      node {
        id
        name
        tagline
        description
        url
        votesCount
        createdAt

        topics(first: 10) {
          edges {
            node {
              name
            }
          }
        }

        website
      }
    }
  }
}
"""


def fetch_producthunt_posts():
    """
    Fetch latest Product Hunt posts using GraphQL API.
    """

    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        GRAPHQL_URL,
        json={"query": QUERY},
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    posts = []

    edges = data["data"]["posts"]["edges"]

    for edge in edges:

        node = edge["node"]

        topics = [
            topic["node"]["name"]
            for topic in node["topics"]["edges"]
        ]

        post = {

            "title": node.get("name", ""),

            "tagline": node.get("tagline", ""),

            "description": node.get("description", ""),

            "topics": topics,

            "votes": node.get("votesCount", 0),

            "created_at": node.get("createdAt", ""),

            "website": node.get("website", ""),

            "link": node.get("url", ""),

            "source": "Product Hunt",

            "type": "product_launch"

        }

        posts.append(post)

    return posts


if __name__ == "__main__":

    posts = fetch_producthunt_posts()

    print(f"\nCollected {len(posts)} Product Hunt posts\n")

    for post in posts:

        print("=" * 60)

        print("Title       :", post["title"])

        print("Tagline     :", post["tagline"])

        print("Votes       :", post["votes"])

        print("Topics      :", ", ".join(post["topics"]))

        print("Website     :", post["website"])

        print("Product Hunt:", post["link"])