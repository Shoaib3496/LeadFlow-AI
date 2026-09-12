from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # -----------------------------------------
    # Marketplace Timestamps
    # -----------------------------------------

    submitted_at = Column(DateTime, nullable=True)

    updated_at = Column(DateTime, nullable=True)

    # -----------------------------------------
    # Opportunity Status
    # -----------------------------------------

    opportunity_status = Column(
        String,
        default="UNKNOWN",
        nullable=False
    )

    source_status = Column(
        String,
        default="",
        nullable=True
    )

    freshness_checked_at = Column(
        DateTime,
        nullable=True
    )

    # Basic Information
    title = Column(String)
    description = Column(String)
    platform = Column(String)
    link = Column(String, nullable=True)

    company_name = Column(String, default="")
    industry = Column(String, default="")
    website = Column(String, default="")
    email = Column(String, default="")
    linkedin = Column(String, default="")
    twitter = Column(String, default="")
    country = Column(String, default="")

    # AI Analysis
    business_type = Column(String)
    lead_category = Column(String)
    service_needed = Column(String)
    technology = Column(String)
    company_stage = Column(String)

    # Business Details
    budget = Column(String)
    urgency = Column(String)

    # Scoring
    lead_score = Column(Integer)
    # Advanced AI Scores
    quality_score = Column(Integer, default=0)

    priority_score = Column(Integer, default=0)

    # -----------------------------------------
    # Commercial Qualification
    # -----------------------------------------

    buyer_intent_score = Column(Integer, default=0)

    business_fit_score = Column(Integer, default=0)

    qualification_score = Column(Integer, default=0)

    commercial_score = Column(Integer, default=0)

    commercial_priority = Column(String, default="LOW")

    primary_service = Column(String, default="")


    # -----------------------------------------
    # Marketplace Information
    # -----------------------------------------

    freelancer_project_id = Column(
        String,
        nullable=True
    )

    budget_min = Column(String, default="")

    budget_max = Column(String, default="")

    currency = Column(String, default="")

    project_type = Column(String, default="")

    bid_count = Column(Integer, default=0)

    marketplace_urgent = Column(Boolean, default=False)


    # -----------------------------------------
    # Source Intelligence
    # -----------------------------------------

    source_type = Column(String, default="")

    source_confidence = Column(Integer, default=0)

    ranking_reason = Column(String, default="")

    # AI Opportunity Detection
    opportunity = Column(String, default="")

    reason = Column(String, default="")

    outreach_strategy = Column(String, default="")
    outreach_message = Column(Text, nullable=True)

    # -----------------------------
    # CRM Fields
    # -----------------------------

    crm_status = Column(String, default="New")

    assigned_to = Column(String, default="Founder")

    contact_name = Column(String, nullable=True)

    contact_email = Column(String, nullable=True)

    contact_phone = Column(String, nullable=True)

    last_contact_date = Column(DateTime, nullable=True)

    next_followup = Column(DateTime, nullable=True)

    notes = Column(Text, nullable=True)

    proposal_sent = Column(Boolean, default=False)

    meeting_scheduled = Column(Boolean, default=False)

    deal_value = Column(Float, default=0.0)

    won = Column(Boolean, default=False)

    lost = Column(Boolean, default=False)


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False)

    category = Column(String, nullable=False)

    country = Column(String, nullable=False)

    enabled = Column(Boolean, default=True)

    # Phase 4 Monitoring
    status = Column(String, default="Active")

    last_run = Column(DateTime, nullable=True)

    leads_collected = Column(Integer, default=0)