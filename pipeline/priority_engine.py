from datetime import datetime, timezone


class PriorityEngine:

    def __init__(self):

        self.source_weights = {
            "GitHub": 95,
            "RemoteOK": 90,
            "HackerNews": 85,
            "ProductHunt": 82,
            "Dev.to": 75,
            "RSS": 70,
        }

    def freshness_score(self, published_at):

        if not published_at:
            return 50

        try:

            published = datetime.fromisoformat(
                published_at.replace("Z", "+00:00")
            )

            now = datetime.now(timezone.utc)

            age_days = (now - published).days

            if age_days <= 1:
                return 100

            if age_days <= 3:
                return 90

            if age_days <= 7:
                return 80

            if age_days <= 30:
                return 70

            return 50

        except Exception:
            return 50

    def calculate_priority(self, lead):

        ai_score = lead.get("score", 0)

        quality_score = lead.get("quality_score", 0)

        source_score = self.source_weights.get(
            lead.get("platform", ""),
            60
        )

        freshness = self.freshness_score(
            lead.get("published_at", "")
        )

        final_score = (

            ai_score * 0.40 +

            quality_score * 0.30 +

            source_score * 0.20 +

            freshness * 0.10

        )

        return round(final_score, 2)