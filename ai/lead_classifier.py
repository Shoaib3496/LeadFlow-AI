BUSINESS_KEYWORDS = [
    "need website",
    "looking for developer",
    "web developer",
    "website redesign",
    "shopify",
    "wordpress",
    "ecommerce",
    "automation",
    "ai chatbot",
    "software development"
]


def classify_lead(title):

    text = title.lower()

    for keyword in BUSINESS_KEYWORDS:
        if keyword in text:
            return "business_lead"

    return "ignore"


if __name__ == "__main__":

    print(classify_lead("Need website for restaurant"))
    print(classify_lead("Software Engineer"))