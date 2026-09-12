import re


class LeadQualityEngine:

    def __init__(self):

        self.high_value_keywords = {
            "website": 15,
            "web application": 15,
            "dashboard": 15,
            "crm": 20,
            "automation": 20,
            "api": 15,
            "python": 10,
            "react": 10,
            "ai": 25,
            "machine learning": 25,
            "chatbot": 20,
            "saas": 20,
            "developer": 10,
            "software": 10,
            "integration": 15,
            "data": 10,
            "cloud": 10
        }

        self.platform_bonus = {
            "GitHub": 15,
            "RemoteOK": 12,
            "HackerNews": 10,
            "ProductHunt": 10,
            "Dev.to": 6,
            "RSS": 4
        }

    def calculate_score(self, lead):

        score = 0

        text = (
            f"{lead.get('title', '')} "
            f"{lead.get('description', '')}"
        ).lower()

        for keyword, value in self.high_value_keywords.items():
            if keyword in text:
                score += value

        score += self.platform_bonus.get(
            lead.get("platform", ""),
            0
        )

        score += min(len(text) // 150, 15)

        return min(score, 100)