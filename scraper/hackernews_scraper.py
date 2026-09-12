import requests
from datetime import datetime

from scraper.base_scraper import BaseScraper
from config.keywords import BUSINESS_KEYWORDS


TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


class HackerNewsScraper(BaseScraper):

    def fetch_leads(self, limit=20):

        try:

            response = requests.get(
                TOP_STORIES_URL,
                timeout=10
            )

            response.raise_for_status()

            story_ids = response.json()

            leads = []

            fetched = 0
            skipped = 0

            # Fetch a larger pool and filter it
            for story_id in story_ids[:100]:

                story = requests.get(
                    ITEM_URL.format(story_id),
                    timeout=10
                ).json()

                if not story:
                    continue

                # Skip deleted/dead stories
                if story.get("deleted") or story.get("dead"):
                    continue

                title = story.get("title", "")
                description = story.get("text", "")

                title_lower = title.lower()

                # Skip Show HN and Ask HN posts
                if title_lower.startswith("show hn"):
                    skipped += 1
                    continue

                if title_lower.startswith("ask hn"):
                    skipped += 1
                    continue

                combined_text = f"{title} {description}".lower()

                # Keep only posts with relevant keywords
                if not any(keyword in combined_text for keyword in BUSINESS_KEYWORDS):
                    skipped += 1
                    continue

                published = ""

                if story.get("time"):
                    published = datetime.fromtimestamp(
                        story["time"]
                    ).isoformat()

                leads.append(

                    self.normalize_lead(

                        title=title,

                        description=description,

                        url=story.get(
                            "url",
                            f"https://news.ycombinator.com/item?id={story_id}"
                        ),

                        platform="Hacker News",

                        author=story.get("by", ""),

                        published_at=published

                    )

                )

                fetched += 1

                # Stop after required number of quality leads
                if fetched >= limit:
                    break

            print(f"HackerNewsScraper:")
            print(f"  Stories Scanned      : 100")
            print(f"  Irrelevant Skipped   : {skipped}")
            print(f"  Business Leads Found : {len(leads)}")

            return leads

        except Exception as e:

            print("Hacker News Error:", e)

            return []


if __name__ == "__main__":

    scraper = HackerNewsScraper()

    leads = scraper.fetch_leads()

    print(f"\nFetched {len(leads)} quality leads\n")

    for lead in leads:

        print("-" * 60)
        print("Title:", lead["title"])
        print("Author:", lead["author"])
        print("Platform:", lead["platform"])
        print("Published:", lead["published_at"])
        print("URL:", lead["url"])