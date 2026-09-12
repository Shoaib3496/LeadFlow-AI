from typing import List
from scraper.base.lead_model import Lead


class LeadDeduplicator:
    """
    Step 4.3.3.3

    Removes duplicate leads from the validated dataset.
    """

    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""

        return " ".join(
            text.lower().strip().split()
        )

    def remove_duplicates(
        self,
        leads: List[Lead]
    ) -> List[Lead]:

        unique = []

        seen_urls = set()
        seen_titles = set()

        duplicate_urls = 0
        duplicate_titles = 0

        for lead in leads:

            normalized_title = self.normalize(
                lead.title
            )

            normalized_url = self.normalize(
                lead.url
            )

            # -------------------------
            # Duplicate URL
            # -------------------------

            if normalized_url in seen_urls:

                duplicate_urls += 1

                continue

            # -------------------------
            # Duplicate Title
            # -------------------------

            if normalized_title in seen_titles:

                duplicate_titles += 1

                continue

            seen_urls.add(normalized_url)

            seen_titles.add(normalized_title)

            unique.append(lead)

        print("\n" + "=" * 60)
        print("DEDUPLICATION")
        print("=" * 60)

        print(f"Input Leads            : {len(leads)}")
        print(f"Duplicate URLs         : {duplicate_urls}")
        print(f"Duplicate Titles       : {duplicate_titles}")
        print(f"Unique Leads           : {len(unique)}")

        return unique