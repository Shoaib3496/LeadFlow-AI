import sys
import os
import json
import ollama
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import OLLAMA_MODEL

PROMPT = """
You are an information extraction system.

Extract ONLY information explicitly present in the text.

DO NOT GUESS.
DO NOT HALLUCINATE.
DO NOT INFER missing values.

If information is missing, return "Unknown".

Return ONLY valid JSON.

Schema:

{
  "business_type": "",
  "lead_category": "",
  "service_needed": "",
  "technology": "",
  "company_stage": "",
  "budget": "",
  "urgency": "",
  "lead_score": 0
}

Allowed lead_category values:

Website Development
AI Automation
Mobile App
CRM
Data Analytics
Cloud
DevOps
API Integration
Custom Software
Unknown

lead_score:

95-100 = Clear client looking to hire

80-94 = Strong buying intent

60-79 = Possible opportunity

40-59 = Weak opportunity

0-39 = Not a business lead

Return ONLY JSON.

Text:

<<TEXT>>
"""

VALID_CATEGORIES = {
    "Website Development",
    "AI Automation",
    "Mobile App",
    "CRM",
    "Data Analytics",
    "Cloud",
    "DevOps",
    "API Integration",
    "Custom Software",
    "Unknown",
}

def clean_json_response(text: str) -> str:
    """
    Cleans Ollama output before JSON parsing.
    """

    # Remove markdown blocks
    text = text.replace("```json", "")
    text = text.replace("```", "")

    # Keep only first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    # Remove JavaScript comments
    text = re.sub(r"//.*", "", text)

    # Convert score ranges into integers
    text = re.sub(
        r'"lead_score"\s*:\s*60-79',
        '"lead_score": 70',
        text
    )

    text = re.sub(
        r'"lead_score"\s*:\s*80-94',
        '"lead_score": 87',
        text
    )

    text = re.sub(
        r'"lead_score"\s*:\s*95-100',
        '"lead_score": 98',
        text
    )

    text = re.sub(
        r'"lead_score"\s*:\s*40-59',
        '"lead_score": 50',
        text
    )

    text = re.sub(
        r'"lead_score"\s*:\s*0-39',
        '"lead_score": 20',
        text
    )

    return text.strip()


def analyze_lead(text):

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

    cleaned = clean_json_response(result)

    try:

        parsed = json.loads(cleaned)

        # Default values

        parsed.setdefault("business_type", "Unknown")
        parsed.setdefault("lead_category", "Unknown")
        parsed.setdefault("service_needed", "Unknown")
        parsed.setdefault("technology", "Unknown")
        parsed.setdefault("company_stage", "Unknown")
        parsed.setdefault("budget", "Unknown")
        parsed.setdefault("urgency", "Unknown")
        parsed.setdefault("lead_score", 0)

        # Convert lists into strings

        for field in [
            "business_type",
            "lead_category",
            "service_needed",
            "technology",
            "company_stage",
            "budget",
            "urgency"
        ]:

            if isinstance(parsed.get(field), list):
                parsed[field] = ", ".join(str(x) for x in parsed[field])

        # Validation

        if parsed.get("lead_category") not in VALID_CATEGORIES:
            parsed["lead_category"] = "Unknown"

        if not parsed.get("technology"):
            parsed["technology"] = "Unknown"

        if not parsed.get("business_type"):
            parsed["business_type"] = "Unknown"

        if not parsed.get("company_stage"):
            parsed["company_stage"] = "Unknown"

        if not parsed.get("budget"):
            parsed["budget"] = "Unknown"

        if not parsed.get("service_needed"):
            parsed["service_needed"] = "Unknown"

        if parsed.get("urgency") not in ["Low", "Medium", "High", "Unknown"]:
            parsed["urgency"] = "Unknown"

        score = parsed.get("lead_score", 0)

        if not isinstance(score, int):
            score = 0

        parsed["lead_score"] = max(0, min(score, 100))

        print("Analyzer JSON Parsed Successfully!")

        return parsed

    except json.JSONDecodeError as e:

        print("\nJSON Parse Failed")
        print("-" * 50)
        print(e)
        print(cleaned)

        return {
            "business_type": "Unknown",
            "lead_category": "Unknown",
            "service_needed": "Unknown",
            "technology": "Unknown",
            "company_stage": "Unknown",
            "budget": "Unknown",
            "urgency": "Unknown",
            "lead_score": 0
        }


if __name__ == "__main__":

    tests = [

        "Need Shopify website for my clothing store",

        "Looking for AI chatbot for customer support",

        "Need a React dashboard for our SaaS",

        "Need CRM software for our company",

        "Looking for mobile app developer",

        "Need WordPress website redesign"

    ]

    for test in tests:

        print("\n" + "=" * 60)
        print(test)
        print(analyze_lead(test))