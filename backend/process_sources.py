import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.source_manager import collect_all_sources
from acquisition.lead_router import route_lead
from ai.ai_classifier import classify_with_ai
from ai.analyzer import analyze_lead
from ai.text_utils import normalize_title
from notifications.notifier import notify_new_lead
from database.db import SessionLocal
from database.models import Lead

db = SessionLocal()

items = collect_all_sources()

saved = 0
ignored = 0
duplicates = 0

# Statistics for every source
source_stats = {}

for item in items:

    source = item.get("source", "Unknown")

    if source not in source_stats:
        source_stats[source] = {
            "collected": 0,
            "saved": 0,
            "ignored": 0,
            "duplicates": 0
        }

    source_stats[source]["collected"] += 1

    # ---------------------------------------------------
    # Product Hunt Filter
    # ---------------------------------------------------

    if (
        item.get("source") == "Product Hunt"
        and item.get("type") == "product_launch"
    ):

        print("\n" + "=" * 60)
        print("SOURCE :", source)
        print("TITLE  :", item["title"])
        print("RESULT : Ignored (Product Launch)")
        print("=" * 60)

        ignored += 1
        source_stats[source]["ignored"] += 1
        continue

    # ---------------------------------------------------
    # AI Classification
    # ---------------------------------------------------

    text = f"""
Title: {item.get("title", "")}

Tagline: {item.get("tagline", "")}

Description: {item.get("description", "")}

Topics: {", ".join(item.get("topics", []))}
"""

    classification = classify_with_ai(text)

    print("\n" + "=" * 60)
    print("SOURCE :", source)
    print("TITLE  :", item.get("title", ""))
    print("CLASSIFICATION :", classification)

    is_business = classification.get("is_business_lead", False)
    confidence = classification.get("confidence", 0)

    if is_business and confidence >= 80:
        item["type"] = "business_lead"
        print(f"RESULT : Business Lead (Confidence: {confidence})")
    else:
        item["type"] = "ignore"
        print(f"RESULT : Ignored (Confidence: {confidence})")

    print("=" * 60)

    # ---------------------------------------------------
    # Route Only Business Leads
    # ---------------------------------------------------

    if not route_lead(item):
        ignored += 1
        source_stats[source]["ignored"] += 1
        continue

    # ---------------------------------------------------
    # Duplicate Detection
    # ---------------------------------------------------

    normalized = normalize_title(item["title"])

    exists = False

    for lead in db.query(Lead).all():

        if normalize_title(lead.title) == normalized:
            exists = True
            break

    if exists:

        print(f"Duplicate Found: {item['title']}")

        duplicates += 1
        source_stats[source]["duplicates"] += 1
        continue

    # ---------------------------------------------------
    # AI Lead Analysis
    # ---------------------------------------------------

    analysis = analyze_lead(text)

    lead = Lead(

        title=item["title"],

        description=item.get(
            "description",
            item["title"]
        ),

        platform=source,

        link=item["link"],

        business_type=analysis["business_type"],

        budget=analysis["budget"],

        urgency=analysis["urgency"],

        lead_score=analysis["lead_score"]

    )

    db.add(lead)

    notify_new_lead(
        item["title"],
        analysis["lead_score"]
    )

    print(f"Saved: {item['title']}")

    saved += 1
    source_stats[source]["saved"] += 1

# ---------------------------------------------------
# Commit Database
# ---------------------------------------------------

db.commit()

# ---------------------------------------------------
# Source Summary
# ---------------------------------------------------

print("\n")
print("=" * 70)
print("SOURCE SUMMARY")
print("=" * 70)

for source, stats in source_stats.items():

    print(f"\n{source}")

    print(f"Collected  : {stats['collected']}")

    print(f"Saved      : {stats['saved']}")

    print(f"Ignored    : {stats['ignored']}")

    print(f"Duplicates : {stats['duplicates']}")

# ---------------------------------------------------
# Overall Summary
# ---------------------------------------------------

print("\n" + "=" * 70)
print("OVERALL SUMMARY")
print("=" * 70)

print(f"Sources Processed   : {len(source_stats)}")

print(f"Total Collected     : {len(items)}")

print(f"New Leads Saved     : {saved}")

print(f"Duplicates Skipped  : {duplicates}")

print(f"Ignored             : {ignored}")

print("=" * 70)