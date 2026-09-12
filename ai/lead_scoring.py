def calculate_score(text):

    score = 0

    text = text.lower()

    if "website" in text:
        score += 30

    if "ecommerce" in text:
        score += 20

    if "business" in text:
        score += 20

    if "developer" in text:
        score += 10

    if "urgent" in text:
        score += 20

    return score