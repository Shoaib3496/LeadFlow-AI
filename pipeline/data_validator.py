from typing import List

from scraper.base.lead_model import Lead


class LeadDataValidator:
    """
    Step 4.3.3.2

    Validates and cleans lead data before deduplication.
    """

    REQUIRED_FIELDS = [
        "title",
        "description",
        "source",
        "url"
    ]

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""

        return " ".join(str(text).strip().split())

    def validate(self, leads: List[Lead]) -> List[Lead]:

        valid_leads = []

        invalid_count = 0

        missing_title = 0
        missing_description = 0
        missing_source = 0
        missing_url = 0
        invalid_url = 0

        for lead in leads:

            # -----------------------
            # Clean fields
            # -----------------------

            lead.title = self._clean_text(lead.title)
            lead.description = self._clean_text(lead.description)
            lead.source = self._clean_text(lead.source)
            lead.url = self._clean_text(lead.url)

            if lead.company:
                lead.company = self._clean_text(lead.company)

            if lead.location:
                lead.location = self._clean_text(lead.location)

            if lead.contact_name:
                lead.contact_name = self._clean_text(lead.contact_name)

            if lead.contact_email:
                lead.contact_email = self._clean_text(lead.contact_email)

            # -----------------------
            # Required fields
            # -----------------------

            if not lead.title:
                missing_title += 1
                invalid_count += 1
                print(f"[INVALID] Missing title -> {lead.source}")
                continue

            if not lead.description:
                missing_description += 1
                lead.description = lead.title

            if not lead.source:
                missing_source += 1
                invalid_count += 1
                print("[INVALID] Missing source")
                continue

            if not lead.url:
                missing_url += 1
                invalid_count += 1
                print(f"[INVALID] Missing URL -> {lead.title}")
                continue

            # -----------------------
            # URL validation
            # -----------------------

            if not (
                lead.url.startswith("http://")
                or lead.url.startswith("https://")
            ):
                invalid_url += 1
                invalid_count += 1
                print(f"[INVALID] Invalid URL -> {lead.title} | {lead.url}")
                continue

            valid_leads.append(lead)

        print("\n" + "=" * 60)
        print("DATA VALIDATION")
        print("=" * 60)
        print(f"Input Leads      : {len(leads)}")
        print(f"Valid Leads      : {len(valid_leads)}")
        print(f"Invalid Removed  : {invalid_count}")
        print("\nValidation Breakdown")
        print("-" * 40)
        print(f"Missing Title       : {missing_title}")
        print(f"Missing Description : {missing_description}")
        print(f"Missing Source      : {missing_source}")
        print(f"Missing URL         : {missing_url}")
        print(f"Invalid URL         : {invalid_url}")

        success_rate = (
            (len(valid_leads) / len(leads)) * 100
            if leads else 0
        )
        print(f"Success Rate        : {success_rate:.2f}%")
        return valid_leads