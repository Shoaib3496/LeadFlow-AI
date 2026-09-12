from database.db import SessionLocal
from database.models import Lead

from ai.lead_filter import is_qualified_lead
from ai.analyzer import analyze_lead
from enrichment.lead_enricher import enrich_lead


def process_posts(posts):

    db = SessionLocal()

    retrieved = len(posts)
    qualified = 0
    ignored = 0
    saved = 0
    duplicates = 0

    for post in posts:

        title = post.get("title", "").strip()

        if not title:
            continue

        # Filter
        if not is_qualified_lead(title):
            ignored += 1
            continue

        qualified += 1

        # Duplicate Check
        existing = db.query(Lead).filter(
            Lead.title == title
        ).first()

        if existing:
            duplicates += 1
            continue

        # AI Analysis
        ai = analyze_lead(title)
        enriched = enrich_lead(post)

        lead = Lead(
            title=title,
            description=post.get("description", ""),
            platform=post.get("platform", "Unknown"),
            link=post.get("link", ""),

            company_name=enriched["company_name"],
            website=enriched["website"],
            email=enriched["email"],
            linkedin=enriched["linkedin"],
            twitter=enriched["twitter"],
            country=enriched["country"],

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

    return {
        "retrieved": retrieved,
        "qualified": qualified,
        "ignored": ignored,
        "saved": saved,
        "duplicates": duplicates
    }