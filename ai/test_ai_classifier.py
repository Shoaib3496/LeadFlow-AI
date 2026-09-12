import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.ai_classifier import classify_with_ai

tests = [

    "Need website for my restaurant.",

    "Looking for Shopify developer.",

    "Software Engineer needed at Google.",

    "OpenAI released a new model.",

    "Need AI chatbot for my business."

]

for text in tests:

    print("\n", text)

    print(classify_with_ai(text))