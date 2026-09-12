from ai.business_lead_classifier import classify_business_lead

tests = [

    "Need website for my restaurant",

    "Looking for AI chatbot developer",

    "Hiring React developer",

    "DiffusionGemma Developer Guide",

    "Weekly Dev Community Discussion",

    "OpenAI releases new model"

]

for text in tests:

    print("=" * 60)

    print(text)

    print(classify_business_lead(text))