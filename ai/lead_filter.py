BUSINESS_KEYWORDS = [

    # Website
    "website",
    "web developer",
    "website redesign",
    "landing page",

    # Ecommerce
    "shopify",
    "woocommerce",
    "ecommerce",

    # Software
    "software",
    "application",
    "mobile app",
    "app developer",
    "saas",

    # AI
    "ai",
    "chatbot",
    "automation",
    "llm",

    # CRM
    "crm",

    # Hiring
    "looking for",
    "need",
    "hire",
    "hiring",
    "developer",
    "freelancer",

    # Business
    "business",
    "startup",
    "agency",
    "client"
]


def is_qualified_lead(text):

    text = text.lower()

    return any(keyword in text for keyword in BUSINESS_KEYWORDS)