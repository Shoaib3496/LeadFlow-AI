from datetime import datetime, timezone


class CommercialOpportunityRanker:

    def calculate(self, lead):

        # ---------------------------------------
        # 1. QUALIFICATION SCORE
        # ---------------------------------------

        qualification = lead.get(
            "qualification_score", 0
        ) or 0

        qualification_component = (
            qualification * 0.30
        )

        # ---------------------------------------
        # 2. COMPETITION SCORE
        # ---------------------------------------

        bids = lead.get("bid_count", 0) or 0

        if bids <= 5:
            competition_score = 100

        elif bids <= 10:
            competition_score = 90

        elif bids <= 25:
            competition_score = 75

        elif bids <= 50:
            competition_score = 55

        elif bids <= 100:
            competition_score = 35

        elif bids <= 200:
            competition_score = 15

        else:
            competition_score = 5

        competition_component = (
            competition_score * 0.25
        )

        # ---------------------------------------
        # 3. BUDGET SCORE
        # ---------------------------------------

        budget_max = lead.get(
            "budget_max", 0
        ) or 0

        currency = (
            lead.get("currency", "")
            or ""
        ).upper()

        budget_score = self._budget_score(
            budget_max,
            currency
        )

        budget_component = (
            budget_score * 0.15
        )

        # ---------------------------------------
        # 4. URGENCY SCORE
        # ---------------------------------------

        urgent = lead.get("urgent", False)

        urgency_score = 100 if urgent else 50

        urgency_component = (
            urgency_score * 0.10
        )

        # ---------------------------------------
        # 5. FRESHNESS SCORE
        # ---------------------------------------

        freshness_score = self._freshness_score(
            lead
        )

        freshness_component = (
            freshness_score * 0.10
        )

        # ---------------------------------------
        # 6. SOURCE CONFIDENCE
        # ---------------------------------------

        source_confidence = lead.get(
            "source_confidence", 90
        ) or 90

        source_component = (
            source_confidence * 0.10
        )

        # ---------------------------------------
        # FINAL SCORE
        # ---------------------------------------

        final_score = (
            qualification_component
            + competition_component
            + budget_component
            + urgency_component
            + freshness_component
            + source_component
        )

        final_score = round(
            min(final_score, 100)
        )

        # ---------------------------------------
        # PRIORITY
        # ---------------------------------------

        if final_score >= 72:
            priority = "HOT"

        elif final_score >= 60:
            priority = "WARM"

        elif final_score >= 45:
            priority = "MEDIUM"

        else:
            priority = "LOW"

        return {

            "commercial_score": final_score,

            "commercial_priority": priority,

            "competition_score":
                competition_score,

            "budget_score":
                budget_score,

            "freshness_score":
                freshness_score,

            "ranking_reason": (
                f"Qualification {qualification}/100 | "
                f"Competition {competition_score}/100 "
                f"({bids} bids) | "
                f"Budget {budget_score}/100 | "
                f"Urgency {urgency_score}/100 | "
                f"Freshness {freshness_score}/100 | "
                f"Source {source_confidence}/100"
            )
        }

    # ==========================================
    # BUDGET SCORING
    # ==========================================

    @staticmethod
    def _budget_score(
        budget_max,
        currency
    ):

        try:
            amount = float(budget_max)

        except (TypeError, ValueError):
            return 30

        # INR

        if currency == "INR":

            if amount >= 100000:
                return 100

            elif amount >= 50000:
                return 90

            elif amount >= 25000:
                return 75

            elif amount >= 10000:
                return 60

            elif amount >= 5000:
                return 40

            return 20

        # USD / CAD / AUD / EUR / GBP
        #
        # We are NOT converting currencies here.
        # These are simply approximate commercial
        # tiers for lead prioritization.

        if amount >= 2000:
            return 100

        elif amount >= 1000:
            return 90

        elif amount >= 500:
            return 75

        elif amount >= 250:
            return 60

        elif amount >= 100:
            return 45

        elif amount >= 50:
            return 30

        return 15

    # ==========================================
    # FRESHNESS
    # ==========================================

    @staticmethod
    def _freshness_score(lead):

        timestamp = (
            lead.get("time_submitted")
            or lead.get("submitdate")
        )

        if not timestamp:
            return 50

        try:

            submitted = datetime.fromtimestamp(
                float(timestamp),
                tz=timezone.utc
            )

            now = datetime.now(
                timezone.utc
            )

            age_hours = (
                now - submitted
            ).total_seconds() / 3600

            if age_hours <= 1:
                return 100

            elif age_hours <= 3:
                return 90

            elif age_hours <= 6:
                return 80

            elif age_hours <= 12:
                return 70

            elif age_hours <= 24:
                return 60

            elif age_hours <= 48:
                return 40

            elif age_hours <= 72:
                return 20

            return 10

        except Exception:
            return 50