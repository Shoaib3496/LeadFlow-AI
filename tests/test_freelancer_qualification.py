from scraper.freelancer_scraper import FreelancerScraper
from ai.buyer_intent import BuyerIntentEngine
from ai.business_fit import BusinessFitEngine


def main():

    print("\n" + "=" * 80)
    print("🚀 LEADFLOW AI — FREELANCER QUALIFICATION TEST")
    print("=" * 80)

    # ---------------------------------------------------------
    # Initialize engines
    # ---------------------------------------------------------

    scraper = FreelancerScraper()

    buyer_engine = BuyerIntentEngine()

    fit_engine = BusinessFitEngine()

    # ---------------------------------------------------------
    # Fetch live Freelancer projects
    # ---------------------------------------------------------

    print("\n📡 Fetching live Freelancer projects...\n")

    leads = scraper.fetch_leads(limit=20)

    print(
        f"\n📥 Freelancer projects collected: {len(leads)}"
    )

    # ---------------------------------------------------------
    # Counters
    # ---------------------------------------------------------

    buyer_rejected = 0
    fit_rejected = 0
    qualified = 0

    qualified_leads = []

    # ---------------------------------------------------------
    # Analyze each project
    # ---------------------------------------------------------

    for lead in leads:

        print("\n" + "=" * 80)

        print(
            "TITLE:",
            lead.get("title", "")
        )

        print(
            "PLATFORM:",
            lead.get("platform", "")
        )

        print(
            "BUDGET:",
            lead.get("budget", "Unknown")
        )

        # -----------------------------------------------------
        # Buyer Intent
        # -----------------------------------------------------

        buyer_result = buyer_engine.analyze(
            lead
        )

        buyer_score = buyer_result[
            "buyer_intent_score"
        ]

        buyer_genuine = buyer_result[
            "is_genuine_opportunity"
        ]

        print(
            "BUYER INTENT SCORE:",
            buyer_score
        )

        print(
            "BUYER INTENT:",
            buyer_result["intent_level"]
        )

        # -----------------------------------------------------
        # Reject if no genuine buyer intent
        # -----------------------------------------------------

        if not buyer_genuine:

            buyer_rejected += 1

            print(
                "❌ RESULT: REJECTED BY BUYER INTENT"
            )

            print(
                "REASON:",
                buyer_result["reason"]
            )

            continue

        # -----------------------------------------------------
        # Business Fit
        # -----------------------------------------------------

        fit_result = fit_engine.analyze(
            lead
        )

        fit_score = fit_result[
            "business_fit_score"
        ]

        print(
            "BUSINESS FIT SCORE:",
            fit_score
        )

        print(
            "BUSINESS FIT LEVEL:",
            fit_result["business_fit_level"]
        )

        print(
            "PRIMARY SERVICE:",
            fit_result["primary_service"]
        )

        # -----------------------------------------------------
        # Reject if not relevant to our business
        # -----------------------------------------------------

        if not fit_result["is_business_fit"]:

            fit_rejected += 1

            print(
                "❌ RESULT: REJECTED BY BUSINESS FIT"
            )

            print(
                "REASON:",
                fit_result["business_fit_reason"]
            )

            continue

        # -----------------------------------------------------
        # Qualified
        # -----------------------------------------------------

        qualified += 1

        # Temporary combined score.
        # This is NOT yet our final production priority score.
        combined_score = round(
            (
                buyer_score * 0.60
            )
            +
            (
                fit_score * 0.40
            )
        )

        lead["buyer_intent_score"] = (
            buyer_score
        )

        lead["business_fit_score"] = (
            fit_score
        )

        lead["qualification_score"] = (
            combined_score
        )

        lead["primary_service"] = (
            fit_result["primary_service"]
        )

        lead["buyer_reason"] = (
            buyer_result["reason"]
        )

        lead["business_fit_reason"] = (
            fit_result["business_fit_reason"]
        )

        qualified_leads.append(
            lead
        )

        print(
            "✅ RESULT: QUALIFIED GENUINE LEAD"
        )

        print(
            "QUALIFICATION SCORE:",
            combined_score
        )

        print(
            "BUYER REASON:",
            buyer_result["reason"]
        )

        print(
            "FIT REASON:",
            fit_result["business_fit_reason"]
        )

    # ---------------------------------------------------------
    # Sort qualified leads
    # ---------------------------------------------------------

    qualified_leads.sort(
        key=lambda x: x.get(
            "qualification_score",
            0
        ),
        reverse=True
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    total = len(leads)

    qualification_rate = (
        (qualified / total) * 100
        if total
        else 0
    )

    print("\n\n" + "=" * 80)

    print(
        "📊 FREELANCER QUALIFICATION SUMMARY"
    )

    print("=" * 80)

    print(
        f"📥 Projects Collected          : {total}"
    )

    print(
        f"❌ Buyer Intent Rejected       : {buyer_rejected}"
    )

    print(
        f"❌ Business Fit Rejected       : {fit_rejected}"
    )

    print(
        f"✅ Genuine Qualified Leads     : {qualified}"
    )

    print(
        f"🎯 Qualification Rate          : "
        f"{qualification_rate:.2f}%"
    )

    print("=" * 80)

    # ---------------------------------------------------------
    # Ranked qualified opportunities
    # ---------------------------------------------------------

    if qualified_leads:

        print(
            "\n🏆 QUALIFIED OPPORTUNITIES\n"
        )

        for index, lead in enumerate(
            qualified_leads,
            start=1
        ):

            print("-" * 80)

            print(
                f"#{index}"
            )

            print(
                "Title:",
                lead.get("title", "")
            )

            print(
                "Budget:",
                lead.get(
                    "budget",
                    "Unknown"
                )
            )

            print(
                "Service:",
                lead.get(
                    "primary_service",
                    "unknown"
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
                "Qualification:",
                lead.get(
                    "qualification_score",
                    0
                )
            )

            print(
                "Bids:",
                lead.get(
                    "bid_count",
                    "Unknown"
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
                "URL:",
                lead.get(
                    "url",
                    ""
                )
            )

    else:

        print(
            "\n⚠️ No qualified opportunities found."
        )


if __name__ == "__main__":
    main()