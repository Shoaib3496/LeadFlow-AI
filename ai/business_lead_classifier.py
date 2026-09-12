import json
import ollama

from config.settings import OLLAMA_MODEL

PROMPT = """
You are an expert B2B lead qualification system.

Your ONLY task is to determine whether the following content represents a REAL BUSINESS OPPORTUNITY for a software development company.

A business opportunity means that a person or company is actively looking for, requesting, or likely to purchase software services.

Examples of TRUE:
- Looking for a web developer
- Need a website
- Hiring software engineers
- Need a CRM
- Need an AI chatbot
- Need automation
- Looking for SaaS development
- Need API integration
- Need mobile app development

Examples of FALSE:
- Tutorials
- Guides
- Blog posts
- Product launches
- Product Hunt listings
- Show HN posts
- Open-source repositories
- GitHub projects
- Research papers
- AI news
- Company announcements
- "Let's connect" networking posts
- Technology discussions
- Framework releases
- Conference talks
- Documentation

IMPORTANT RULES

Return TRUE ONLY if the content clearly indicates buying intent or a request for software services.

If uncertain, return FALSE.

Return ONLY valid JSON in this format:

{
    "is_business_lead": true,
    "reason": "short explanation"
}

Content:

<<TEXT>>
"""


def classify_business_lead(text):

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": PROMPT.replace("<<TEXT>>", text)
            }
        ]
    )

    result = response["message"]["content"]

    cleaned = (
        result.replace("```json", "")
        .replace("```", "")
        .strip()
    )

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1:
        cleaned = cleaned[start:end + 1]

    try:
        parsed = json.loads(cleaned)

        return {
            "is_business_lead": bool(parsed.get("is_business_lead", False)),
            "reason": parsed.get("reason", "")
        }

    except Exception:

        return {
            "is_business_lead": False,
            "reason": "Invalid AI response"
        }


if __name__ == "__main__":

    tests = [

        "Need Shopify website for my clothing store",

        "Looking for React developer",

        "Hiring AI engineer",

        "Show HN: My new project",

        "Introducing Gemma 4",

        "Hey DEV, let's connect."

    ]

    for test in tests:

        print("=" * 60)
        print(test)
        print(classify_business_lead(test))