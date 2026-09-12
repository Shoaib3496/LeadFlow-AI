from scraper.freelancer_scraper import FreelancerScraper
from ai.buyer_intent import BuyerIntentEngine


def main():

    print("\n" + "=" * 80)
    print("FREELANCER → BUYER INTENT TEST")
    print("=" * 80)

    scraper = FreelancerScraper()

    intent_engine = BuyerIntentEngine()

    # Fetch live Freelancer opportunities
    leads = scraper.fetch_leads(limit=20)

    genuine = 0
    rejected = 0

    results = []

    for lead in leads:

        result = intent_engine.analyze(lead)

        lead["buyer_intent_score"] = result[
            "buyer_intent_score"
        ]

        lead["intent_level"] = result[
            "intent_level"
        ]

        lead["is_genuine_opportunity"] = result[
            "is_genuine_opportunity"
        ]

        results.append(
            (
                lead,
                result
            )
        )

        if result["is_genuine_opportunity"]:
            genuine += 1
        else:
            rejected += 1

    # --------------------------------------------------
    # Sort highest buyer intent first
    # --------------------------------------------------

    results.sort(
        key=lambda item:
        item[1]["buyer_intent_score"],
        reverse=True
    )

    # --------------------------------------------------
    # Display results
    # --------------------------------------------------

    for lead, result in results:

        print("\n" + "=" * 80)

        if result["is_genuine_opportunity"]:

            print("✅ GENUINE OPPORTUNITY")

        else:

            print("❌ REJECTED")

        print(
            "Title:",
            lead.get("title")
        )

        print(
            "Budget:",
            lead.get("budget")
        )

        print(
            "Project Type:",
            lead.get("project_type")
        )

        print(
            "Source:",
            lead.get("platform")
        )

        print(
            "Source Confidence:",
            lead.get(
                "source_confidence"
            )
        )

        print(
            "Buyer Intent Score:",
            result["buyer_intent_score"]
        )

        print(
            "Intent Level:",
            result["intent_level"]
        )

        print(
            "Reason:",
            result["reason"]
        )

        print(
            "Jobs:",
            lead.get("job_names")
        )

        print(
            "Description:",
            (
                lead.get(
                    "description",
                    ""
                )[:300]
            )
        )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print("\n")
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    print(
        f"Freelancer Projects : {len(leads)}"
    )

    print(
        f"Genuine Opportunities: {genuine}"
    )

    print(
        f"Rejected             : {rejected}"
    )

    if leads:

        rate = (
            genuine /
            len(leads)
        ) * 100

    else:

        rate = 0

    print(
        f"Acceptance Rate      : {rate:.2f}%"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()