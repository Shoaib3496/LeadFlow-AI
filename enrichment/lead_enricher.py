import re


def extract_company_name(title):

    title = title.strip()

    # Remove anything after separators
    title = re.split(r"[-:|]", title)[0]

    return title.strip()


def enrich_lead(post):

    company = extract_company_name(
        post.get("title", "")
    )

    return {
        "company_name": company,
        "website": "",
        "email": "",
        "linkedin": "",
        "twitter": "",
        "country": ""
    }