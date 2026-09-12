import requests
from datetime import datetime
from typing import List

from scraper.base.base_scraper import BaseScraper
from scraper.base.lead_model import Lead
from config.keywords import BUSINESS_KEYWORDS


TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


class HackerNewsScraper(BaseScraper):

    def __init__(self):
        super().__init__("Hacker News")

    def scrape(self) -> List[Lead]:

        response = requests.get(
            TOP_STORIES_URL,
            timeout=10
        )

        response.raise_for_status()

        story_ids = response.json()

        leads = []

        fetched = 0
        skipped = 0

        for story_id in story_ids[:100]:

            try:
                story = requests.get(
                    ITEM_URL.format(story_id),
                    timeout=10
                ).json()
            except Exception:
                continue

            if not story:
                continue

            if story.get("deleted") or story.get("dead"):
                continue

            title = story.get("title", "")
            description = story.get("text", "")

            title_lower = title.lower()

            if title_lower.startswith("show hn"):
                skipped += 1
                continue

            if title_lower.startswith("ask hn"):
                skipped += 1
                continue

            combined = f"{title} {description}".lower()

            if not any(
                keyword in combined
                for keyword in BUSINESS_KEYWORDS
            ):
                skipped += 1
                continue

            published = ""

            if story.get("time"):
                published = datetime.fromtimestamp(
                    story["time"]
                ).isoformat()

            leads.append(
                Lead(
                    title=title,
                    description=description,
                    source="Hacker News",
                    url=story.get(
                        "url",
                        f"https://news.ycombinator.com/item?id={story_id}"
                    ),
                    posted_at=published,
                    contact_name=story.get("by", ""),
                    raw_data=story
                )
            )

            fetched += 1

            if fetched >= 20:
                break

        print("HackerNewsScraper:")
        print("  Stories Scanned      : 100")
        print(f"  Irrelevant Skipped   : {skipped}")
        print(f"  Business Leads Found : {len(leads)}")

        return leads