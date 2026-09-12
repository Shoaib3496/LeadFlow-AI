import re


def enrich_lead(lead):

    title = lead.get("title", "")
    description = lead.get("description", "")

    text = f"{title} {description}"

    company = "Unknown"

    # Example patterns
    patterns = [
        r"for\s+([A-Z][A-Za-z0-9& ]+)",
        r"at\s+([A-Z][A-Za-z0-9& ]+)",
        r"company\s+([A-Z][A-Za-z0-9& ]+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            company = match.group(1).strip()
            break

    lead["company_name"] = company

    lead.setdefault("industry", "Unknown")
    lead.setdefault("website", "Unknown")
    lead.setdefault("country", "Unknown")
    lead.setdefault("email", "Unknown")
    lead.setdefault("linkedin", "Unknown")
    lead.setdefault("twitter", "Unknown")

    return lead