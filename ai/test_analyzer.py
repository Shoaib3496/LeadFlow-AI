from analyzer import analyze_lead
import json

lead = """
Need ecommerce website for clothing store.
Budget around $3000.
Need within 2 weeks.
"""

result = analyze_lead(lead)

print(result)