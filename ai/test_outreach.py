from ai.outreach_generator import generate_outreach

lead = {
    "title": "Need website for my restaurant",
    "business_type": "Restaurant",
    "budget": "$3000",
    "urgency": "High"
}

print(generate_outreach(lead))