from lead_scoring import calculate_score

lead = """
Need ecommerce website for my business.
Looking for a developer urgently.
"""

score = calculate_score(lead)

print("Lead Score:", score)