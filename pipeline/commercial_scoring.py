from typing import List
from scraper.base.lead_model import Lead


class CommercialScoringEngine:
    """
    Step 4.3.3.5

    Converts AI-qualified leads into commercially ranked opportunities.
    """

    HIGH_INTENT_PHRASES = [
        "looking for",
        "need a",
        "need an",
        "need someone",
        "seeking",
        "want to hire",
        "looking to hire",
        "hiring developer",
        "hire a developer",
        "hire developer",
        "need developer",
        "need help",
        "looking for developer",
        "looking for freelancer",
        "looking for agency",
        "seeking developer",
        "seeking freelancer",
        "seeking agency",
        "build a website",
        "build an app",
        "build a dashboard",
        "build a crm",
        "develop a website",
        "develop an app",
        "redesign website",
        "integrate api"
    ]

    MEDIUM_INTENT_PHRASES = [
        "project",
        "requirement",
        "required",
        "developer needed",
        "freelancer",
        "contractor",
        "consultant",
        "implementation",
        "integration",
        "redesign",
        "migration",
        "automation"
    ]

    NON_BUYER_PHRASES = [
        "tutorial",
        "guide",
        "how to",
        "introduction to",
        "explained",
        "newsletter",
        "research",
        "benchmark",
        "release",
        "announces",
        "announcement",
        "opinion",
        "video",
        "course",
        "documentation"
    ]

    TARGET_CATEGORIES = {
        "Website Development",
        "AI Automation",
        "Mobile App",
        "CRM",
        "Data Analytics",
        "Cloud",
        "DevOps",
        "API Integration",
        "Custom Software"
    }

    SERVICE_MAP = {
        "Website Development": "Website Development",
        "AI Automation": "AI & Automation",
        "Mobile App": "Mobile App Development",
        "CRM": "CRM Development",
        "Data Analytics": "Data Analytics",
        "Cloud": "Cloud Services",
        "DevOps": "DevOps",
        "API Integration": "API Integration",
        "Custom Software": "Custom Software Development"
    }

    @staticmethod
    def _text(lead: Lead) -> str:
        return (
            f"{lead.title or ''} "
            f"{lead.description or ''} "
            f"{getattr(lead, 'service_needed', '') or ''}"
        ).lower()

    def calculate_buyer_intent(self, lead: Lead) -> int:

        text = self._text(lead)

        score = 0

        # Strong explicit buying signals
        for phrase in self.HIGH_INTENT_PHRASES:
            if phrase in text:
                score += 25

        # Weaker commercial signals
        for phrase in self.MEDIUM_INTENT_PHRASES:
            if phrase in text:
                score += 10

        # AI lead score contributes, but cannot dominate
        ai_score = getattr(lead, "lead_score", 0) or 0

        if ai_score >= 80:
            score += 20
        elif ai_score >= 60:
            score += 15
        elif ai_score >= 40:
            score += 5

        # Budget is a valuable buying signal
        budget = str(
            getattr(lead, "budget", "") or ""
        ).strip().lower()

        if budget not in ["", "unknown", "none", "n/a"]:
            score += 15

        # Urgency
        urgency = str(
            getattr(lead, "urgency", "") or ""
        ).lower()

        if urgency == "high":
            score += 15
        elif urgency == "medium":
            score += 8

        # Penalize obvious informational content
        for phrase in self.NON_BUYER_PHRASES:
            if phrase in text:
                score -= 15

        return max(0, min(score, 100))

    def calculate_business_fit(self, lead: Lead) -> int:

        score = 0

        category = getattr(
            lead,
            "lead_category",
            "Unknown"
        )

        if category in self.TARGET_CATEGORIES:
            score += 50

        service = str(
            getattr(lead, "service_needed", "") or ""
        ).lower()

        if service not in [
            "",
            "unknown",
            "none",
            "n/a"
        ]:
            score += 20

        technology = str(
            getattr(lead, "technology", "") or ""
        ).lower()

        if technology not in [
            "",
            "unknown",
            "none",
            "n/a"
        ]:
            score += 15

        business_type = str(
            getattr(lead, "business_type", "") or ""
        ).lower()

        if business_type not in [
            "",
            "unknown",
            "none",
            "n/a"
        ]:
            score += 15

        return min(score, 100)

    def calculate_qualification(
        self,
        buyer_intent: int,
        business_fit: int
    ) -> int:

        return round(
            buyer_intent * 0.60
            + business_fit * 0.40
        )

    @staticmethod
    def calculate_commercial_score(
        qualification_score: int,
        ai_score: int
    ) -> int:

        ai_score = ai_score or 0

        return round(
            qualification_score * 0.75
            + ai_score * 0.25
        )

    @staticmethod
    def get_priority(score: int) -> str:

        if score >= 80:
            return "HOT"

        if score >= 60:
            return "WARM"

        if score >= 40:
            return "MEDIUM"

        return "LOW"

    def get_primary_service(self, lead: Lead) -> str:

        category = getattr(
            lead,
            "lead_category",
            "Unknown"
        )

        return self.SERVICE_MAP.get(
            category,
            "Unknown"
        )

    @staticmethod
    def build_ranking_reason(
        buyer_intent: int,
        business_fit: int,
        commercial_score: int,
        priority: str
    ) -> str:

        if priority == "HOT":
            return (
                "Strong buyer intent and strong business fit. "
                "High-priority commercial opportunity."
            )

        if priority == "WARM":
            return (
                "Good commercial potential with meaningful "
                "buyer intent or service fit."
            )

        if priority == "MEDIUM":
            return (
                "Possible commercial opportunity, but buyer "
                "intent or business fit requires verification."
            )

        if buyer_intent < 20:
            return (
                "Low explicit buyer intent. Likely informational, "
                "technical, hiring, product, or non-client content."
            )

        return (
            "Weak commercial signals. Manual verification "
            "recommended before outreach."
        )

    def score_lead(self, lead: Lead) -> Lead:

        buyer_intent = self.calculate_buyer_intent(lead)

        business_fit = self.calculate_business_fit(lead)

        qualification = self.calculate_qualification(
            buyer_intent,
            business_fit
        )

        commercial = self.calculate_commercial_score(
            qualification,
            getattr(lead, "lead_score", 0)
        )

        priority = self.get_priority(commercial)

        lead.buyer_intent_score = buyer_intent
        lead.business_fit_score = business_fit
        lead.qualification_score = qualification
        lead.commercial_score = commercial
        lead.commercial_priority = priority

        lead.primary_service = self.get_primary_service(
            lead
        )

        lead.ranking_reason = self.build_ranking_reason(
            buyer_intent,
            business_fit,
            commercial,
            priority
        )

        return lead

    def score_all(
        self,
        leads: List[Lead]
    ) -> List[Lead]:

        for lead in leads:
            self.score_lead(lead)

        leads.sort(
            key=lambda lead: lead.commercial_score,
            reverse=True
        )

        hot = sum(
            1 for lead in leads
            if lead.commercial_priority == "HOT"
        )

        warm = sum(
            1 for lead in leads
            if lead.commercial_priority == "WARM"
        )

        medium = sum(
            1 for lead in leads
            if lead.commercial_priority == "MEDIUM"
        )

        low = sum(
            1 for lead in leads
            if lead.commercial_priority == "LOW"
        )

        print("\n" + "=" * 60)
        print("COMMERCIAL SCORING SUMMARY")
        print("=" * 60)

        print(f"Total Leads : {len(leads)}")
        print(f"HOT         : {hot}")
        print(f"WARM        : {warm}")
        print(f"MEDIUM      : {medium}")
        print(f"LOW         : {low}")

        return leads