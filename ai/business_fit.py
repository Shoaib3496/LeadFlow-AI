import re


class BusinessFitEngine:

    # =========================================================
    # HIGH-VALUE SERVICES
    # =========================================================

    HIGH_VALUE_SERVICES = {

        "website": [
            "website development",
            "website design",
            "web development",
            "web application",
            "web app",
            "web portal",
            "landing page",
        ],

        "ecommerce": [
            "ecommerce",
            "e-commerce",
            "shopify",
            "woocommerce",
            "online store",
        ],

        "wordpress": [
            "wordpress",
            "elementor",
            "woocommerce",
        ],

        "custom_software": [
            "custom software",
            "software development",
            "software application",
            "platform development",
            "portal development",
        ],

        "frontend": [
            "react",
            "react.js",
            "next.js",
            "vue",
            "angular",
            "frontend development",
            "front-end development",
        ],

        "backend": [
            "python",
            "django",
            "flask",
            "fastapi",
            "node.js",
            "nodejs",
            "laravel",
            "backend development",
            "back-end development",
        ],

        "api": [
            "api integration",
            "api development",
            "rest api",
            "backend api",
        ],

        "automation": [
            "automation",
            "workflow automation",
            "business automation",
            "process automation",
        ],

        "ai": [
            "artificial intelligence",
            "machine learning",
            "ai chatbot",
            "chatbot",
            "ai automation",
            "rag",
            "llm",
        ],

        "data_engineering": [
            "data pipeline",
            "etl",
            "data engineering",
            "data warehouse",
            "data integration",
        ],

        "dashboard": [
            "dashboard development",
            "analytics dashboard",
            "business dashboard",
            "power bi",
        ],
    }

    # =========================================================
    # NON-TARGET SERVICES
    # =========================================================

    NON_TARGET_SERVICES = {

        "data_entry": [
            "data entry",
            "copy typing",
            "typing job",
            "spreadsheet cleanup",
            "data entry assistant",
        ],

        "sales": [
            "telemarketing",
            "call center",
            "sales representative",
            "sales agent",
            "cold calling",
        ],

        "writing": [
            "copywriting",
            "ghostwriting",
            "article writing",
            "content writer",
            "blog writing",
        ],

        "customer_support": [
            "customer service",
            "customer support",
            "virtual assistant",
        ],

        "research_only": [
            "market research",
            "market study",
            "research report",
            "academic research",
            "scientific research",
        ],

        "marketing_only": [
            "performance marketer",
            "facebook marketing",
            "google ads",
            "social media marketing",
            "seo specialist",
            "link building",
        ],
    }

    # =========================================================
    # UNSUITABLE / DO-NOT-PURSUE WORK
    # =========================================================

    UNSUITABLE_SIGNALS = [
        "unlock invite-only",
        "bypass",
        "crack",
        "steal",
        "credential theft",
        "phishing",
        "malware",
        "ransomware",
        "ddos",
        "reverse engineer protected",
        "circumvent",
    ]

    @staticmethod
    def _normalize(text):

        text = str(text or "").lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    @staticmethod
    def _find_matches(text, phrases):

        return [
            phrase
            for phrase in phrases
            if phrase in text
        ]

    def analyze(self, lead):

        title = self._normalize(
            lead.get("title", "")
        )

        description = self._normalize(
            lead.get("description", "")
        )

        jobs = lead.get(
            "job_names",
            []
        ) or []

        job_text = self._normalize(
            " ".join(
                str(job)
                for job in jobs
            )
        )

        text = (
            title
            + " "
            + description
            + " "
            + job_text
        )

        # =====================================================
        # TARGET SERVICE MATCHING
        # =====================================================

        target_matches = {}

        for category, phrases in self.HIGH_VALUE_SERVICES.items():

            matches = self._find_matches(
                text,
                phrases
            )

            if matches:

                target_matches[
                    category
                ] = matches

        # =====================================================
        # NON-TARGET MATCHING
        # =====================================================

        non_target_matches = {}

        for category, phrases in self.NON_TARGET_SERVICES.items():

            matches = self._find_matches(
                text,
                phrases
            )

            if matches:

                non_target_matches[
                    category
                ] = matches

        # =====================================================
        # SUITABILITY
        # =====================================================

        unsuitable_matches = self._find_matches(
            text,
            self.UNSUITABLE_SIGNALS
        )

        # =====================================================
        # SCORE
        # =====================================================

        score = 0

        # Each meaningful target service adds value.
        score += min(
            len(target_matches) * 20,
            80
        )

        # Extra points when the project clearly requires
        # several related technical capabilities.
        total_target_signals = sum(
            len(matches)
            for matches in target_matches.values()
        )

        if total_target_signals >= 3:
            score += 10

        if total_target_signals >= 5:
            score += 10

        # Penalize non-target work.
        score -= min(
            len(non_target_matches) * 25,
            75
        )

        # Strongly reject unsuitable work.
        if unsuitable_matches:
            score = 0

        score = max(
            0,
            min(score, 100)
        )

        # =====================================================
        # FIT CLASSIFICATION
        # =====================================================

        if score >= 70:
            fit_level = "Excellent"

        elif score >= 50:
            fit_level = "Strong"

        elif score >= 30:
            fit_level = "Good"

        elif score >= 20:
            fit_level = "Relevant"

        else:
            fit_level = "Poor"

        # =====================================================
        # FINAL DECISION
        # =====================================================

        # =====================================================
        # FINAL BUSINESS FIT DECISION
        # =====================================================

        # A project does not need many different technologies
        # to be commercially valuable.
        #
        # Example:
        # "Build a business website"
        # may only match the website category, but it is still
        # exactly the type of work we want.

        strong_target_categories = {
            "website",
            "ecommerce",
            "wordpress",
            "custom_software",
            "frontend",
            "backend",
            "api",
            "automation",
            "ai",
            "data_engineering",
            "dashboard",
        }

        matched_categories = set(
            target_matches.keys()
        )

        has_strong_target_service = bool(
            matched_categories
            & strong_target_categories
        )

        is_business_fit = (
            has_strong_target_service
            and not unsuitable_matches
        )

        # Reject projects that are primarily non-target work
        # and only contain an incidental technical keyword.
        if (
            non_target_matches
            and len(target_matches) <= 1
        ):
            is_business_fit = False
        # If the project is overwhelmingly a non-target service,
        # don't accept it just because a technical keyword
        # appears somewhere.
        if (
            len(non_target_matches) > 0
            and len(target_matches) <= 1
        ):
            is_business_fit = False

        # =====================================================
        # PRIMARY SERVICE
        # =====================================================

        if target_matches:

            primary_service = next(
                iter(target_matches)
            )

        else:

            primary_service = "unknown"

        # =====================================================
        # REASON
        # =====================================================

        reasons = []

        if target_matches:

            reasons.append(
                "Target services: "
                + ", ".join(
                    target_matches.keys()
                )
            )

        if non_target_matches:

            reasons.append(
                "Non-target services: "
                + ", ".join(
                    non_target_matches.keys()
                )
            )

        if unsuitable_matches:

            reasons.append(
                "Unsuitable signals: "
                + ", ".join(
                    unsuitable_matches[:3]
                )
            )

        if not reasons:

            reasons.append(
                "No target business services detected"
            )

        return {

            "business_fit_score":
                score,

            "business_fit_level":
                fit_level,

            "is_business_fit":
                is_business_fit,

            "primary_service":
                primary_service,

            "target_services":
                list(
                    target_matches.keys()
                ),

            "target_matches":
                target_matches,

            "non_target_services":
                list(
                    non_target_matches.keys()
                ),

            "unsuitable_signals":
                unsuitable_matches,

            "business_fit_reason":
                " | ".join(reasons),
        }


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    engine = BusinessFitEngine()

    test_leads = [

        {
            "title":
                "Shopify Booking Landing Page",

            "description":
                "Need Shopify landing page development",

            "job_names": [
                "Shopify",
                "Web Development",
                "PHP"
            ]
        },

        {
            "title":
                "Social Media Data Entry",

            "description":
                "Need data entry and Excel work",

            "job_names": [
                "Data Entry",
                "Excel",
                "Data Analysis"
            ]
        },

        {
            "title":
                "Demo Trading Platform Bridge",

            "description":
                "Web based trading platform with API development",

            "job_names": [
                "PHP",
                "Web Development",
                "Backend Development",
                "API Development"
            ]
        },

        {
            "title":
                "Vendedor Call Center",

            "description":
                "Looking for sales and call center worker",

            "job_names": [
                "Telemarketing",
                "Sales",
                "CRM"
            ]
        }
    ]

    for lead in test_leads:

        result = engine.analyze(
            lead
        )

        print(
            "\n",
            "=" * 70
        )

        print(
            "TITLE:",
            lead["title"]
        )

        print(
            "FIT SCORE:",
            result["business_fit_score"]
        )

        print(
            "FIT LEVEL:",
            result["business_fit_level"]
        )

        print(
            "BUSINESS FIT:",
            result["is_business_fit"]
        )

        print(
            "PRIMARY SERVICE:",
            result["primary_service"]
        )

        print(
            "REASON:",
            result["business_fit_reason"]
        )