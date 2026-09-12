import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.hackernews_scraper import fetch_hackernews_posts
from ai.analyzer import analyze_lead

from database.db import SessionLocal
from database.models import Lead
from ai.lead_filter import is_qualified_lead

db = SessionLocal()

posts = fetch_hackernews_posts(20)

qualified = 0
ignored = 0
saved = 0
duplicates = 0

for post in posts:

    # Filter non-business posts
    if not is_qualified_lead(post["title"]):
        ignored += 1
        continue

    qualified += 1

    # Check if lead already exists
    existing = db.query(Lead).filter(
        Lead.title == post["title"]
    ).first()

    if existing:
        duplicates += 1
        continue

    # Analyze with AI
    ai = analyze_lead(post["title"])

    lead = Lead(
        title=post["title"],
        description=post["description"],
        platform=post["platform"],
        link=post["link"],
        business_type=ai["business_type"],
        lead_category=ai["lead_category"],
        service_needed=ai["service_needed"],
        technology=ai["technology"],
        company_stage=ai["company_stage"],
        budget=ai["budget"],
        urgency=ai["urgency"],
        lead_score=ai["lead_score"],
        status="New"
    )

    db.add(lead)
    saved += 1

db.commit()

print()

print("\n========== SUMMARY ==========")
print(f"Posts Retrieved : {len(posts)}")
print(f"Qualified Leads : {qualified}")
print(f"Ignored Posts   : {ignored}")
print(f"Saved           : {saved}")
print(f"Duplicates      : {duplicates}")
print("=============================")