import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal
from database.models import Lead

db = SessionLocal()

# Clear existing sample data (optional during development)
db.query(Lead).delete()

sample_leads = [

    {
        "title": "Need Shopify Store for Clothing Brand",
        "description": "Looking for Shopify developer",
        "platform": "Reddit",
        "business_type": "Ecommerce",
        "budget": "$3000",
        "urgency": "High",
        "lead_score": 92,
        "status": "New"
    },

    {
        "title": "Need AI Chatbot for Customer Support",
        "description": "Looking for AI automation",
        "platform": "Product Hunt",
        "business_type": "SaaS",
        "budget": "$5000",
        "urgency": "High",
        "lead_score": 88,
        "status": "New"
    },

    {
        "title": "Restaurant Website Development",
        "description": "Need website redesign",
        "platform": "Hacker News",
        "business_type": "Restaurant",
        "budget": "$2500",
        "urgency": "Medium",
        "lead_score": 81,
        "status": "Contacted"
    },

    {
        "title": "CRM System for Sales Team",
        "description": "Need CRM implementation",
        "platform": "Dev.to",
        "business_type": "General Business",
        "budget": "$8000",
        "urgency": "Medium",
        "lead_score": 77,
        "status": "Proposal Sent"
    },

    {
        "title": "Need Mobile App for Food Delivery",
        "description": "Android & iOS application",
        "platform": "Reddit",
        "business_type": "Startup",
        "budget": "$12000",
        "urgency": "High",
        "lead_score": 95,
        "status": "New"
    }

]

for item in sample_leads:

    lead = Lead(
        title=item["title"],
        description=item["description"],
        platform=item["platform"],
        business_type=item["business_type"],
        budget=item["budget"],
        urgency=item["urgency"],
        lead_score=item["lead_score"],
        status=item["status"],
        link=""
    )

    db.add(lead)

db.commit()

print("✅ Sample leads inserted successfully!")