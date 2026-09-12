from typing import List

from scraper.base.lead_model import Lead

from ai.analyzer import analyze_lead


class AIQualificationPipeline:
    """
    Step 4.3.3.4

    Runs AI qualification on validated leads.
    """

    def qualify(
        self,
        leads: List[Lead]
    ) -> List[Lead]:

        print("\n" + "=" * 60)
        print("AI QUALIFICATION")
        print("=" * 60)

        total = len(leads)
        classified = 0
        unknown = 0

        for index, lead in enumerate(leads, start=1):

            print(
                f"[{index}/{total}] "
                f"{lead.title}"
            )

            text = f"""

Title:
{lead.title}

Description:
{lead.description}

"""

            result = analyze_lead(text)

            if result["lead_category"] == "Unknown":
                unknown += 1
            else:
                classified += 1

            lead.business_type = result["business_type"]

            lead.lead_category = result["lead_category"]

            lead.service_needed = result["service_needed"]

            lead.technology = result["technology"]

            lead.company_stage = result["company_stage"]

            lead.budget = result["budget"]

            lead.urgency = result["urgency"]

            lead.lead_score = result["lead_score"]

        classification_rate = (
            (classified / total) * 100
            if total > 0 else 0
        )

        print("\n" + "=" * 60)
        print("AI QUALIFICATION SUMMARY")
        print("=" * 60)

        print(f"Processed Leads   : {total}")
        print(f"Classified Leads  : {classified}")
        print(f"Unknown Leads     : {unknown}")
        print(f"Classification Rate : {classification_rate:.2f}%")
        return leads