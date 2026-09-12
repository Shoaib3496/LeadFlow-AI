import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ollama
import json

from config.settings import OLLAMA_MODEL

PROMPT = """
You are an expert business lead qualification AI.

Your ONLY task is to determine whether the text contains a REAL BUSINESS BUYING INTENT.

A business lead means that a person or company is actively looking to BUY or HIRE digital services.

Return ONLY valid JSON.

{
    "is_business_lead": true,
    "confidence": 95,
    "reason": ""
}

Return TRUE ONLY if the text clearly indicates someone wants to hire, buy, or outsource services such as:

- Website development
- Web application development
- Mobile app development
- Shopify development
- WordPress development
- AI chatbot
- AI automation
- CRM implementation
- SaaS development
- UI/UX design
- Software development
- API integration
- Data engineering
- Data analytics
- Cloud consulting
- DevOps consulting

Examples that MUST return TRUE:

- Need website for my restaurant
- Looking for Shopify developer
- Need AI chatbot
- Want to redesign our company website
- Looking for software agency
- Need freelancer for app development
- Need automation for my business

Return FALSE if the text is:

- News
- Blog
- Tutorial
- Open-source project
- GitHub repository
- Product launch
- Show HN post
- Company announcement
- Technical article
- Research paper
- Hiring employees
- Job posting
- Recruiting
- Educational content
- Opinion article
- Startup showcase

IMPORTANT:

A company BUILDING software is NOT a business lead.

A person LOOKING TO HIRE someone to build software IS a business lead.

If there is any doubt, return FALSE.

Text:
"""


def classify_with_ai(text):

    # -------------------------------------------------
    # Fast Pre-Filter
    # -------------------------------------------------

    lower_text = text.lower()

    job_keywords = [
        "is hiring",
        "hiring",
        "software engineer",
        "backend engineer",
        "back end engineer",
        "frontend engineer",
        "front end engineer",
        "full stack engineer",
        "machine learning engineer",
        "product manager",
        "head of engineering",
        "growth marketer",
        "founding engineer",
        "developer advocate",
        "devrel engineer",
        "fpga engineer"
    ]

    for keyword in job_keywords:

        if keyword in lower_text:

            return {
                "is_business_lead": False,
                "confidence": 100,
                "reason": "Detected as a job posting (Pre-Filter)"
            }

    announcement_keywords = [
        "show hn",
        "github",
        "open-source",
        "opensource",
        "released",
        "launch",
        "launches",
        "blog",
        "tutorial",
        "research",
        "paper",
        "benchmark",
        "comparison",
        "notes",
    ]

    for keyword in announcement_keywords:

        if keyword in lower_text:

            return {
                "is_business_lead": False,
                "confidence": 100,
                "reason": "Announcement/Project (Pre-Filter)"
            }

    # -------------------------------------------------
    # AI Classification
    # -------------------------------------------------

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": PROMPT + text
            }
        ]
    )

    result = response["message"]["content"]

    print("\n========== AI CLASSIFIER RAW ==========\n")
    print(result)
    print("\n=======================================\n")

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

        parsed.setdefault("is_business_lead", False)
        parsed.setdefault("confidence", 0)
        parsed.setdefault("reason", "Not provided")

        print("Classifier JSON Parsed Successfully!")

        return parsed

    except Exception as e:

        print("Classifier JSON Error:", e)
        print("Returned Text:")
        print(cleaned)

        return {
            "is_business_lead": False,
            "confidence": 0,
            "reason": "Parsing failed"
        }


if __name__ == "__main__":

    tests = [

        # TRUE

        "Need website for my restaurant",

        "Looking for Shopify developer",

        "Need AI chatbot for my business",

        "Want to redesign our company website",

        "Need mobile app for food delivery",

        "Looking for software agency",

        "Need CRM implementation",

        "Need automation for customer support",

        "Need WordPress developer",

        "Need SaaS development team",

        # FALSE

        "Software Engineer needed at Google",

        "Startup is hiring Full Stack Engineer",

        "Show HN: My AI startup",

        "GitHub Freno",

        "Software Bonkers",

        "Notes on Software Quality",

        "OpenAI released GPT-6",

        "Blog: AI Trends 2026",

        "Tutorial: Learn Python",

        "Research paper on Machine Learning"

    ]

    for test in tests:

        print("\n--------------------------------")
        print(test)
        print(classify_with_ai(test))