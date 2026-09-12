import re

class BuyerIntentEngine:

    # =========================================================
    # SOURCES
    # =========================================================

    # Sources where the content itself is normally a posted
    # commercial project/request.
    MARKETPLACE_SOURCES = {
        "freelancer",
        "upwork",
        "peopleperhour",
        "guru",
    }

    # Sources that commonly contain articles, discussions,
    # repositories, bugs, news, etc.
    CONTENT_SOURCES = {
        "dev.to",
        "hacker news",
        "product hunt",
        "github",
    }

    # =========================================================
    # STRONG BUYER INTENT
    # =========================================================

    STRONG_INTENT = [
        "looking for a developer",
        "looking for developer",
        "looking for someone",
        "looking to hire",
        "looking for a freelancer",
        "looking for freelancer",

        "need a developer",
        "need developer",
        "need someone",
        "need a website",
        "need website",
        "need an app",
        "need a mobile app",
        "need software",
        "need a system",
        "need a platform",
        "need a portal",
        "need a dashboard",
        "need help building",
        "need help with",

        "want to hire",
        "want someone to",
        "want a website",
        "want a web",
        "want an app",
        "want a platform",

        "seeking developer",
        "seeking a developer",
        "seeking freelancer",
        "seeking a freelancer",
        "seeking an agency",
        "seeking an experienced",

        "hiring developer",
        "hiring a developer",
        "hire a developer",
        "hire developer",

        "freelancer needed",
        "developer needed",
        "developer required",
        "agency needed",
        "contract developer",

        "looking for an agency",

        "we need",
        "i need",
        "we want",
        "i want",
        "we are looking for",
        "i am looking for",
        "i'm looking for",
    ]

    # =========================================================
    # TARGET SERVICES
    # =========================================================

    PROJECT_SIGNALS = [

        # Website
        "website",
        "web development",
        "web developer",
        "web application",
        "web app",
        "landing page",
        "web portal",

        # Ecommerce
        "ecommerce",
        "e-commerce",
        "shopify",
        "woocommerce",

        # CMS
        "wordpress",

        # Frontend
        "react",
        "react.js",
        "next.js",
        "vue",
        "angular",
        "frontend developer",
        "front-end developer",

        # Backend
        "python",
        "python developer",
        "django",
        "flask",
        "fastapi",
        "node.js",
        "nodejs",
        "php",
        "laravel",
        "backend developer",
        "back-end developer",

        # Full stack
        "full stack developer",
        "full-stack developer",

        # Mobile
        "mobile app",
        "android app",
        "ios app",
        "flutter",
        "react native",

        # Business Software
        "crm",
        "erp",
        "saas",
        "custom software",
        "software development",

        # Automation / API
        "automation",
        "api integration",
        "api development",

        # AI
        "ai chatbot",
        "chatbot",
        "ai automation",
        "artificial intelligence",
        "machine learning",

        # Data
        "dashboard",
        "data analytics",
        "data analysis",
    ]

    # =========================================================
    # COMMERCIAL SIGNALS
    # =========================================================

    COMMERCIAL_SIGNALS = [
        "budget",
        "paid",
        "payment",
        "contract",
        "freelance",
        "freelancer",
        "client",
        "project",
        "quote",
        "proposal",
        "price",
        "cost",
        "hourly",
        "fixed price",
        "fixed-price",
    ]

    # =========================================================
    # URGENCY
    # =========================================================

    URGENCY_SIGNALS = [
        "urgent",
        "urgently",
        "asap",
        "immediately",
        "this week",
        "this month",
        "deadline",
        "quickly",
        "soon",
    ]

    # =========================================================
    # NEGATIVE CONTENT
    # =========================================================

    # These are primarily negative when the source is an
    # article/news/discussion source.
    #
    # Notice that "course" has intentionally been removed.
    # "Educational Course Platform Development" can be a real
    # software-development project.
    NEGATIVE_CONTENT_SIGNALS = [
        "tutorial",
        "how to",
        "documentation",
        "docs:",
        "show hn",
        "research paper",
        "release notes",
        "changelog",
        "introducing",
        "announcement",
        "product launch",
        "new release",
        "developer guide",
        "conference",
        "podcast",
        "newsletter",
    ]

    # =========================================================
    # NON-TARGET SERVICES
    # =========================================================

    NON_TARGET_SIGNALS = [
        "data entry",
        "copywriting",
        "ghostwriting",
        "article writing",
        "telemarketing",
        "call center",
        "sales representative",
        "customer service assistant",
        "virtual assistant",
        "translation",
    ]

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _contains(text, phrases):

        return [
            phrase
            for phrase in phrases
            if phrase in text
        ]

    @staticmethod
    def _normalize_source(source):

        return (
            str(source or "")
            .strip()
            .lower()
        )

    @staticmethod
    def _has_real_budget(lead):

        budget = lead.get("budget")

        if budget is None:
            return False

        budget_text = str(budget).strip().lower()

        if budget_text in {
            "",
            "unknown",
            "none",
            "n/a",
            "0",
        }:
            return False

        return True

    # =========================================================
    # ANALYZE
    # =========================================================

    def analyze(self, lead):

        title = lead.get("title", "") or ""

        description = (
            lead.get("description", "")
            or ""
        )

        platform = self._normalize_source(
            lead.get("platform", "")
        )

        text = (
            f"{title} {description}"
        ).lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        # -----------------------------------------------------
        # Detect source type
        # -----------------------------------------------------

        is_marketplace = (
            platform
            in self.MARKETPLACE_SOURCES
        )

        is_content_source = (
            platform
            in self.CONTENT_SOURCES
        )

        # -----------------------------------------------------
        # Text signals
        # -----------------------------------------------------

        strong_matches = self._contains(
            text,
            self.STRONG_INTENT
        )

        project_matches = self._contains(
            text,
            self.PROJECT_SIGNALS
        )

        commercial_matches = self._contains(
            text,
            self.COMMERCIAL_SIGNALS
        )

        urgency_matches = self._contains(
            text,
            self.URGENCY_SIGNALS
        )

        negative_matches = self._contains(
            text,
            self.NEGATIVE_CONTENT_SIGNALS
        )

        non_target_matches = self._contains(
            text,
            self.NON_TARGET_SIGNALS
        )

        # -----------------------------------------------------
        # Structured marketplace evidence
        # -----------------------------------------------------

        source_confidence = lead.get(
            "source_confidence",
            0
        ) or 0

        try:
            source_confidence = int(
                source_confidence
            )
        except (TypeError, ValueError):
            source_confidence = 0

        has_budget = self._has_real_budget(
            lead
        )

        project_type = (
            str(
                lead.get(
                    "project_type",
                    ""
                )
                or ""
            )
            .strip()
            .lower()
        )

        has_project_type = (
            project_type
            in {
                "fixed",
                "hourly",
            }
        )

        urgent_flag = bool(
            lead.get(
                "urgent",
                False
            )
        )

        job_names = (
            lead.get(
                "job_names",
                []
            )
            or []
        )

        job_text = " ".join(
            str(job)
            for job in job_names
        ).lower()

        job_service_matches = (
            self._contains(
                job_text,
                self.PROJECT_SIGNALS
            )
        )

        # Merge service evidence from description/title
        # and structured Freelancer skills.
        all_project_matches = list(
            dict.fromkeys(
                project_matches
                + job_service_matches
            )
        )

        # -----------------------------------------------------
        # SCORING
        # -----------------------------------------------------

        score = 0

        # Strong explicit buying language
        score += min(
            len(strong_matches) * 30,
            60
        )

        # Relevant software/service requirement
        score += min(
            len(all_project_matches) * 8,
            24
        )

        # Commercial words in text
        score += min(
            len(commercial_matches) * 8,
            16
        )

        # Urgency language
        score += min(
            len(urgency_matches) * 6,
            12
        )

        # =====================================================
        # MARKETPLACE SOURCE EVIDENCE
        # =====================================================

        if is_marketplace:

            # An open Freelancer-style project itself is
            # commercial evidence.
            score += 20

            if source_confidence >= 80:
                score += 10

            if has_budget:
                score += 12

            if has_project_type:
                score += 5

            if urgent_flag:
                score += 8

        # =====================================================
        # NEGATIVE CONTENT
        # =====================================================

        # Article-like signals matter much more on content
        # sources than marketplaces.
        if negative_matches:

            if is_content_source:

                score -= min(
                    len(negative_matches) * 25,
                    75
                )

            elif not is_marketplace:

                score -= min(
                    len(negative_matches) * 15,
                    45
                )

            else:

                # Marketplace project descriptions can contain
                # words such as "guide" legitimately.
                score -= min(
                    len(negative_matches) * 5,
                    15
                )

        # =====================================================
        # NON-TARGET SERVICE PENALTY
        # =====================================================

        if (
            non_target_matches
            and not all_project_matches
        ):

            score -= 35

        # Clamp
        score = max(
            0,
            min(score, 100)
        )

        # =====================================================
        # BUSINESS FIT
        # =====================================================

        has_service_fit = (
            len(all_project_matches) > 0
        )

        # Marketplace commercial evidence
        marketplace_commercial_evidence = (

            is_marketplace

            and (

                has_budget
                or has_project_type
                or source_confidence >= 80

            )
        )

        # General web-source commercial evidence
        general_commercial_evidence = (

            len(strong_matches) > 0

            or len(commercial_matches) > 0
        )

        has_commercial_evidence = (

            marketplace_commercial_evidence

            or general_commercial_evidence
        )

        # =====================================================
        # FINAL CLASSIFICATION
        # =====================================================

        if score >= 75:

            intent_level = "High"

        elif score >= 50:

            intent_level = "Medium"

        elif score >= 30:

            intent_level = "Low"

        else:

            intent_level = "None"

        is_genuine_opportunity = (

            score >= 50

            and has_service_fit

            and has_commercial_evidence

        )

        # Explicitly block obviously non-target work when there
        # is no meaningful software-service requirement.
        if (
            non_target_matches
            and not has_service_fit
        ):

            is_genuine_opportunity = False

        # =====================================================
        # REASONS
        # =====================================================

        reasons = []

        if is_marketplace:

            reasons.append(
                f"Marketplace source: {lead.get('platform')}"
            )

        if source_confidence >= 80:

            reasons.append(
                f"Source confidence: {source_confidence}"
            )

        if strong_matches:

            reasons.append(
                "Buying intent: "
                + ", ".join(
                    strong_matches[:3]
                )
            )

        if all_project_matches:

            reasons.append(
                "Service need: "
                + ", ".join(
                    all_project_matches[:4]
                )
            )

        if commercial_matches:

            reasons.append(
                "Commercial signal: "
                + ", ".join(
                    commercial_matches[:3]
                )
            )

        if has_budget:

            reasons.append(
                f"Budget available: {lead.get('budget')}"
            )

        if has_project_type:

            reasons.append(
                f"Project type: {project_type}"
            )

        if urgent_flag:

            reasons.append(
                "Marketplace urgent flag"
            )

        if urgency_matches:

            reasons.append(
                "Urgency: "
                + ", ".join(
                    urgency_matches[:3]
                )
            )

        if non_target_matches:

            reasons.append(
                "Non-target signal: "
                + ", ".join(
                    non_target_matches[:3]
                )
            )

        if negative_matches:

            reasons.append(
                "Negative content signal: "
                + ", ".join(
                    negative_matches[:3]
                )
            )

        if not reasons:

            reasons.append(
                "No meaningful buyer-intent signals detected"
            )

        return {

            "buyer_intent_score":
                score,

            "intent_level":
                intent_level,

            "is_genuine_opportunity":
                is_genuine_opportunity,

            "service_fit":
                has_service_fit,

            "source_type":
                (
                    "marketplace"
                    if is_marketplace
                    else "content"
                    if is_content_source
                    else "other"
                ),

            "has_budget":
                has_budget,

            "strong_signals":
                strong_matches,

            "project_signals":
                all_project_matches,

            "commercial_signals":
                commercial_matches,

            "urgency_signals":
                urgency_matches,

            "negative_signals":
                negative_matches,

            "non_target_signals":
                non_target_matches,

            "reason":
                " | ".join(reasons),
        }


# =============================================================
# LOCAL TEST
# =============================================================

if __name__ == "__main__":

    engine = BuyerIntentEngine()

    test_leads = [

        {
            "title":
                "Need Shopify developer for our clothing store",

            "description":
                "We have a budget and need someone to build "
                "our ecommerce website this month.",

            "platform":
                "Unknown"
        },

        {
            "title":
                "Minimalist WordPress PO Portal",

            "description":
                "I need a brand-new WordPress site that "
                "issues and tracks purchase orders.",

            "platform":
                "Freelancer",

            "budget":
                "250 - 750 AUD",

            "project_type":
                "fixed",

            "source_confidence":
                90,

            "job_names": [
                "WordPress",
                "PHP",
                "Web Development"
            ]
        },

        {
            "title":
                "Python 3.15 Developer Guide",

            "description":
                "A tutorial explaining new Python features.",

            "platform":
                "Dev.to"
        },

        {
            "title":
                "Social Media Data Entry",

            "description":
                "I need someone to enter information into "
                "spreadsheets.",

            "platform":
                "Freelancer",

            "budget":
                "750 - 1250 INR",

            "project_type":
                "hourly",

            "source_confidence":
                90,

            "job_names": [
                "Data Entry",
                "Excel"
            ]
        }
    ]

    for lead in test_leads:

        print("\n" + "=" * 70)

        print(
            "TITLE:",
            lead["title"]
        )

        result = engine.analyze(
            lead
        )

        print(
            "SCORE:",
            result["buyer_intent_score"]
        )

        print(
            "INTENT:",
            result["intent_level"]
        )

        print(
            "SERVICE FIT:",
            result["service_fit"]
        )

        print(
            "GENUINE OPPORTUNITY:",
            result["is_genuine_opportunity"]
        )

        print(
            "REASON:",
            result["reason"]
        )