from scraper.freelancer_scraper import FreelancerScraper
from ai.buyer_intent import BuyerIntentEngine
from ai.business_fit import BusinessFitEngine
from pipeline.commercial_ranker import CommercialOpportunityRanker


def main():

    print("\n" + "=" * 80)
    print("🚀 LEADFLOW AI — COMMERCIAL OPPORTUNITY RANKING")
    print("=" * 80)

    scraper = FreelancerScraper()
    buyer_engine = BuyerIntentEngine()
    fit_engine = BusinessFitEngine()
    ranker = CommercialOpportunityRanker()

    # ---------------------------------------------------------
    # Fetch live Freelancer opportunities
    # ---------------------------------------------------------

    print("\n📡 Fetching live Freelancer projects...\n")

    leads = scraper.fetch_leads(limit=20)

    print("\n🔍 FRESHNESS DEBUG")

    for lead in leads[:5]:

        print("-" * 60)

        print(
            "Title:",
            lead.get("title")
        )

        print(
            "submitdate:",
            lead.get("submitdate")
        )

        print(
            "time_submitted:",
            lead.get("time_submitted")
        )

        print(
            "time_updated:",
            lead.get("time_updated")
        )

        print(
            "published_at:",
            lead.get("published_at")
        )

    print(f"\n📥 Projects collected: {len(leads)}")

    qualified_leads = []

    buyer_rejected = 0
    fit_rejected = 0

    # ---------------------------------------------------------
    # Qualification
    # ---------------------------------------------------------

    for lead in leads:

        # Buyer Intent
        buyer_result = buyer_engine.analyze(lead)

        if not buyer_result["is_genuine_opportunity"]:
            buyer_rejected += 1
            continue

        # Business Fit
        fit_result = fit_engine.analyze(lead)

        if not fit_result["is_business_fit"]:
            fit_rejected += 1
            continue

        buyer_score = buyer_result[
            "buyer_intent_score"
        ]

        fit_score = fit_result[
            "business_fit_score"
        ]

        # -----------------------------------------------------
        # Qualification score
        # -----------------------------------------------------

        qualification_score = round(
            (buyer_score * 0.60)
            +
            (fit_score * 0.40)
        )

        lead["buyer_intent_score"] = buyer_score

        lead["business_fit_score"] = fit_score

        lead["qualification_score"] = (
            qualification_score
        )

        lead["primary_service"] = fit_result.get(
            "primary_service",
            "unknown"
        )

        # -----------------------------------------------------
        # Commercial Ranking
        # -----------------------------------------------------

        ranking = ranker.calculate(lead)

        lead.update(ranking)

        qualified_leads.append(lead)

    # ---------------------------------------------------------
    # Sort by COMMERCIAL score
    # ---------------------------------------------------------

    qualified_leads.sort(
        key=lambda x: x.get(
            "commercial_score",
            0
        ),
        reverse=True
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("📊 COMMERCIAL RANKING SUMMARY")
    print("=" * 80)

    print(
        f"📥 Projects Collected      : {len(leads)}"
    )

    print(
        f"❌ Buyer Intent Rejected   : {buyer_rejected}"
    )

    print(
        f"❌ Business Fit Rejected   : {fit_rejected}"
    )

    print(
        f"✅ Qualified Opportunities : {len(qualified_leads)}"
    )

    print("=" * 80)

    # ---------------------------------------------------------
    # Ranked results
    # ---------------------------------------------------------

    if not qualified_leads:

        print("\n⚠️ No qualified opportunities found.")

        return

    print("\n🏆 COMMERCIAL OPPORTUNITIES\n")

    for index, lead in enumerate(
        qualified_leads,
        start=1
    ):

        priority = lead.get(
            "commercial_priority",
            "LOW"
        )

        if priority == "HOT":
            icon = "🔥"

        elif priority == "WARM":
            icon = "🟡"

        elif priority == "MEDIUM":
            icon = "🔵"

        else:
            icon = "⚪"

        print("=" * 80)

        print(
            f"#{index} {icon} {priority}"
        )

        print(
            "Title:",
            lead.get("title", "")
        )

        print(
            "Platform:",
            lead.get("platform", "")
        )

        print(
            "Service:",
            lead.get(
                "primary_service",
                "unknown"
            )
        )

        print(
            "Budget:",
            lead.get(
                "budget",
                "Unknown"
            )
        )

        print(
            "Qualification:",
            lead.get(
                "qualification_score",
                0
            )
        )

        print(
            "Buyer Intent:",
            lead.get(
                "buyer_intent_score",
                0
            )
        )

        print(
            "Business Fit:",
            lead.get(
                "business_fit_score",
                0
            )
        )

        print(
            "Bids:",
            lead.get(
                "bid_count",
                0
            )
        )

        print(
            "Competition Score:",
            lead.get(
                "competition_score",
                0
            )
        )

        print(
            "Budget Score:",
            lead.get(
                "budget_score",
                0
            )
        )

        print(
            "Freshness Score:",
            lead.get(
                "freshness_score",
                0
            )
        )

        print(
            "Urgent:",
            lead.get(
                "urgent",
                False
            )
        )

        print(
            "COMMERCIAL SCORE:",
            lead.get(
                "commercial_score",
                0
            )
        )

        print(
            "Reason:",
            lead.get(
                "ranking_reason",
                ""
            )
        )

        print(
            "URL:",
            lead.get(
                "url",
                ""
            )
        )

    print("\n" + "=" * 80)
    print("🎯 BEST OPPORTUNITY")
    print("=" * 80)

    best = qualified_leads[0]

    print(
        "Title:",
        best.get("title", "")
    )

    print(
        "Commercial Score:",
        best.get(
            "commercial_score",
            0
        )
    )

    print(
        "Priority:",
        best.get(
            "commercial_priority",
            ""
        )
    )

    print(
        "Bids:",
        best.get(
            "bid_count",
            0
        )
    )

    print(
        "Budget:",
        best.get(
            "budget",
            "Unknown"
        )
    )

    print(
        "URL:",
        best.get(
            "url",
            ""
        )
    )


if __name__ == "__main__":
    main()