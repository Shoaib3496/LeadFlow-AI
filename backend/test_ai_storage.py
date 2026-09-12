import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.analyzer import analyze_lead

lead = """
Need ecommerce website for clothing store.
Budget around $3000.
Need within 2 weeks.
"""

result = analyze_lead(lead)

print(result)