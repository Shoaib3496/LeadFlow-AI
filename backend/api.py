import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from fastapi import Form
from datetime import datetime, date
from fastapi import Depends
from sqlalchemy.orm import Session
from database.db import get_db
from config.settings import CORS_ORIGINS

from backend.auth import router as auth_router
from fastapi.routing import APIRoute
from database.models import Source
from backend.schemas import SourceUpdate, SourceCreate
from backend.scraper_manager import run_enabled_scrapers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, case
from database.db import SessionLocal
from database.models import Lead, Source

from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException

from scraper.mock_leads import sample_posts
from ai.lead_filter import is_qualified_lead
from ai.lead_scoring import calculate_score

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from fastapi import Query
from fastapi.responses import FileResponse
import csv

import threading
from pipeline.scraper_health import scraper_health

from pipeline.production_pipeline import ProductionLeadPipeline
from pipeline.performance_monitor import dashboard_performance

from ai.outreach_generator import generate_outreach

from pipeline.pipeline_status import (
    get_pipeline_status,
    mark_running,
    mark_completed,
    mark_failed
)

app = FastAPI()

@app.middleware("http")
async def performance_middleware(request: Request, call_next):

    start_time = time.perf_counter()

    response = await call_next(request)

    if request.url.path == "/dashboard":
        duration = time.perf_counter() - start_time
        dashboard_performance.record(duration)

    return response

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# PRODUCTION PIPELINE BACKGROUND WORKER
# ============================================================

def production_pipeline_worker():

    try:

        pipeline = ProductionLeadPipeline()

        result = pipeline.run()

        mark_completed(result)

    except Exception as e:

        mark_failed(e)

class LeadStatusUpdate(BaseModel):
    status: str

class CRMStateUpdate(BaseModel):
    proposal_sent: Optional[bool] = None
    meeting_scheduled: Optional[bool] = None
    outcome: Optional[str] = None

templates = Jinja2Templates(directory="dashboard/templates")



@app.get("/")
def home():
    return {"message": "LeadFlow AI API Running"}

@app.get("/scraper-health")
def get_scraper_health():

    health = scraper_health.get_all()

    return {
        "total_scrapers": len(health),
        "healthy": sum(
            1
            for item in health
            if item["status"] == "HEALTHY"
        ),
        "degraded": sum(
            1
            for item in health
            if item["status"] == "DEGRADED"
        ),
        "failed": sum(
            1
            for item in health
            if item["status"] == "FAILED"
        ),
        "scrapers": health
    }

# ============================================================
# PIPELINE STATUS
# ============================================================

@app.get("/pipeline-status")
def pipeline_status():

    return get_pipeline_status()

@app.get("/pipeline-logs")
def get_pipeline_logs(limit: int = 100):

    try:

        # Prevent excessively large requests
        limit = max(1, min(limit, 500))

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(
            "logs",
            f"pipeline_{today}.log"
        )

        if not os.path.exists(log_file):

            return {
                "count": 0,
                "logs": [],
                "message": "Pipeline log file not found."
            }

        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as file:

            lines = file.readlines()

        # Only latest entries
        latest_logs = lines[-limit:]

        # Remove empty lines
        latest_logs = [
            line.strip()
            for line in latest_logs
            if line.strip()
        ]

        return {
            "count": len(latest_logs),
            "logs": latest_logs
        }

    except Exception as e:

        return {
            "count": 0,
            "logs": [],
            "error": str(e)
        }

# =========================================================
# DASHBOARD PERFORMANCE
# STEP 4.3.4.8.2
# =========================================================

@app.get("/dashboard-performance")
def get_dashboard_performance():

    return dashboard_performance.get_status()

# ============================================================
# START PRODUCTION PIPELINE
# ============================================================

@app.post("/run-production-pipeline")
def run_production_pipeline():

    status = get_pipeline_status()

    if status["state"] == "RUNNING":

        return {
            "status": "already_running",
            "message": "Production pipeline is already running."
        }

    mark_running()

    thread = threading.Thread(
        target=production_pipeline_worker,
        daemon=True
    )

    try:

        thread.start()

    except Exception as e:

        mark_failed(e)

        return {
            "status": "failed",
            "message": str(e)
        }

    return {
        "status": "started",
        "message": "Production pipeline started successfully."
    }


@app.get("/leads")
def get_leads(
    search: str = Query(None),
    platform: str = Query(None),
    status: str = Query(None),
    opportunity_status: str = Query(None),
    min_score: int = Query(0),
    sort: str = Query("score_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):

    db = SessionLocal()

    query = db.query(Lead)

    if search:
        query = query.filter(
            Lead.title.ilike(f"%{search}%")
        )

    if platform:
        query = query.filter(
            Lead.platform == platform
        )

    if status:
        query = query.filter(
            Lead.crm_status == status
        )

    if opportunity_status:
        query = query.filter(
            Lead.opportunity_status == opportunity_status
        )

    query = query.filter(
        Lead.lead_score >= min_score
    )

    if sort == "recent":
        query = query.order_by(Lead.id.desc())

    elif sort == "score_asc":
        query = query.order_by(
            Lead.lead_score.asc(),
            Lead.id.desc()
        )

    elif sort == "title_asc":
        query = query.order_by(
            Lead.title.asc(),
            Lead.id.desc()
        )

    elif sort == "title_desc":
        query = query.order_by(
            Lead.title.desc(),
            Lead.id.desc()
        )

    else:
        query = query.order_by(
            Lead.lead_score.desc(),
            Lead.id.desc()
        )

    total = query.count()

    offset = (page - 1) * page_size

    leads = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": lead.id,

                "title": lead.title,

                "platform": lead.platform,

                "link": lead.link,

                "crm_status": lead.crm_status,
                "opportunity_status": lead.opportunity_status,

                # Existing
                "lead_score": lead.lead_score,
                "quality_score": lead.quality_score,
                "priority_score": lead.priority_score,

                # Commercial Intelligence
                "buyer_intent_score": lead.buyer_intent_score,
                "business_fit_score": lead.business_fit_score,
                "qualification_score": lead.qualification_score,
                "commercial_score": lead.commercial_score,
                "priority_score": lead.priority_score,
                "commercial_priority": lead.commercial_priority,

                # Service
                "primary_service": lead.primary_service,

                # Budget
                "budget": lead.budget,
                "budget_min": lead.budget_min,
                "budget_max": lead.budget_max,
                "currency": lead.currency,

                # Marketplace
                "bid_count": lead.bid_count,
                "project_type": lead.project_type,
                "marketplace_urgent": lead.marketplace_urgent,

                # Source
                "source_type": lead.source_type,
                "source_confidence": lead.source_confidence,

                # Opportunity Freshness
                "freshness_checked_at": (
                    lead.freshness_checked_at.isoformat()
                    if lead.freshness_checked_at
                    else None
                ),

                # AI Explanation
                "ranking_reason": lead.ranking_reason
            }
            for lead in leads
        ]
    }

@app.get("/lead/{lead_id}")
def get_lead(lead_id: int):

    db = SessionLocal()

    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return {
        "id": lead.id,
        "title": lead.title,
        "description": lead.description,
        "platform": lead.platform,
        "business_type": lead.business_type,
        "lead_category": lead.lead_category,
        "service_needed": lead.service_needed,
        "technology": lead.technology,
        "company_stage": lead.company_stage,
        "budget": lead.budget,
        "urgency": lead.urgency,
        "lead_score": lead.lead_score,
        "crm_status": lead.crm_status,
        "link": lead.link,
        "company_name": lead.company_name,
        "industry": lead.industry,
        "website": lead.website,
        "email": lead.email,
        "linkedin": lead.linkedin,
        "twitter": lead.twitter,
        "country": lead.country,
        "buyer_intent_score": lead.buyer_intent_score,
        "business_fit_score": lead.business_fit_score,
        "qualification_score": lead.qualification_score,
        "commercial_score": lead.commercial_score,
        "priority_score": lead.priority_score,
        "commercial_priority": lead.commercial_priority,

        "primary_service": lead.primary_service,

        "budget_min": lead.budget_min,
        "budget_max": lead.budget_max,
        "currency": lead.currency,

        "bid_count": lead.bid_count,
        "project_type": lead.project_type,
        "marketplace_urgent": lead.marketplace_urgent,

        "source_type": lead.source_type,
        "source_confidence": lead.source_confidence,

        "ranking_reason": lead.ranking_reason,

        "outreach_strategy": lead.outreach_strategy,

        "submitted_at": lead.submitted_at,
        "updated_at": lead.updated_at,

        # -----------------------------------------
        # Opportunity Status
        # -----------------------------------------
        "opportunity_status": lead.opportunity_status,
        "source_status": lead.source_status,
        "freshness_checked_at": lead.freshness_checked_at,

        "assigned_to": lead.assigned_to,
        "notes": lead.notes,
        "last_contact_date": lead.last_contact_date,
        "next_followup": lead.next_followup,
        "deal_value": lead.deal_value,
        "outreach_message": lead.outreach_message,
        "proposal_sent": lead.proposal_sent,
        "meeting_scheduled": lead.meeting_scheduled,
        "won": lead.won,
        "lost": lead.lost
    }


@app.get("/top-leads")
def get_top_leads():

    db = SessionLocal()

    try:

        leads = (
            db.query(Lead)
            .filter(
                Lead.commercial_score.isnot(None),
                Lead.commercial_score >= 40
            )
            .order_by(
                Lead.commercial_score.desc(),
                Lead.buyer_intent_score.desc(),
                Lead.business_fit_score.desc(),
                Lead.id.desc()
            )
            .limit(5)
            .all()
        )

        return [
            {
                "id": lead.id,
                "title": lead.title,
                "platform": lead.platform,
                "link": lead.link,

                "crm_status": lead.crm_status,

                "commercial_score": lead.commercial_score,
                "priority_score": lead.priority_score,
                "commercial_priority": lead.commercial_priority,
                "buyer_intent_score": lead.buyer_intent_score,
                "business_fit_score": lead.business_fit_score,
                "qualification_score": lead.qualification_score,

                "lead_score": lead.lead_score,
                "priority_score": lead.priority_score,
                "quality_score": lead.quality_score,

                "primary_service": lead.primary_service,

                "budget": lead.budget,
                "budget_min": lead.budget_min,
                "budget_max": lead.budget_max,
                "currency": lead.currency,

                "bid_count": lead.bid_count,
                "project_type": lead.project_type,
                "marketplace_urgent": lead.marketplace_urgent,

                "source_type": lead.source_type,
                "source_confidence": lead.source_confidence,

                "ranking_reason": lead.ranking_reason,

                "business_type": lead.business_type,
                "urgency": lead.urgency,
                "company_name": lead.company_name,
                "country": lead.country,
                "website": lead.website,
                "opportunity": lead.opportunity
            }
            for lead in leads
        ]

    finally:
        db.close()


@app.post("/process-leads")
def process_leads():

    db = SessionLocal()

    saved_count = 0

    for post in sample_posts:

        if is_qualified_lead(post):

            score = calculate_score(post)

            lead = Lead(
                title=post,
                description=post,
                platform="API Source",
                budget="Unknown",
                business_type="Pending AI Analysis",
                urgency="Pending",
                lead_score=score
            )

            db.add(lead)
            saved_count += 1

    db.commit()

    return {
        "status": "success",
        "saved_leads": saved_count
    }

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):


    db = SessionLocal()

    try:

        # ==========================================
        # TOTAL DATABASE LEADS
        # ==========================================

        total_stored_leads = (
            db.query(func.count(Lead.id))
            .scalar()
            or 0
        )


        # ==========================================
        # TOP ACTIONABLE OPPORTUNITIES
        # ==========================================

        leads = (
            db.query(Lead)
            .filter(
                Lead.commercial_score >= 40
            )
            .order_by(
                Lead.commercial_score.desc(),
                Lead.buyer_intent_score.desc(),
                Lead.business_fit_score.desc()
            )
            .limit(50)
            .all()
        )


        # ==========================================
        # DASHBOARD ANALYTICS — OPTIMIZED
        # ==========================================

        analytics_counts = (
            db.query(

                func.sum(
                    case(
                        (
                            Lead.commercial_score >= 40,
                            1
                        ),
                        else_=0
                    )
                ).label("actionable"),

                func.sum(
                    case(
                        (
                            Lead.commercial_priority == "HOT",
                            1
                        ),
                        else_=0
                    )
                ).label("hot"),

                func.sum(
                    case(
                        (
                            Lead.commercial_priority == "WARM",
                            1
                        ),
                        else_=0
                    )
                ).label("warm"),

                func.sum(
                    case(
                        (
                            Lead.commercial_priority == "MEDIUM",
                            1
                        ),
                        else_=0
                    )
                ).label("medium"),

                func.sum(
                    case(
                        (
                            Lead.commercial_priority == "LOW",
                            1
                        ),
                        else_=0
                    )
                ).label("low")

            )
            .one()
        )


        actionable_leads = (
            analytics_counts.actionable or 0
        )

        analytics_hot = (
            analytics_counts.hot or 0
        )

        analytics_warm = (
            analytics_counts.warm or 0
        )

        analytics_medium = (
            analytics_counts.medium or 0
        )

        analytics_low = (
            analytics_counts.low or 0
        )


        # ==========================================
        # DISPLAYED OPPORTUNITY PRIORITY COUNTS
        # ==========================================

        hot_leads = sum(
            1 for lead in leads
            if lead.commercial_priority == "HOT"
        )

        warm_leads = sum(
            1 for lead in leads
            if lead.commercial_priority == "WARM"
        )

        medium_leads = sum(
            1 for lead in leads
            if lead.commercial_priority == "MEDIUM"
        )


        # ==========================================
        # PRODUCTION SOURCES
        # ==========================================

        platforms = {
            lead.platform
            for lead in leads
            if lead.platform
        }

        production_sources = len(platforms)


        # ==========================================
        # BEST / AVERAGE ACTIONABLE SCORE
        # ==========================================

        best_score = max(
            (
                lead.commercial_score or 0
                for lead in leads
            ),
            default=0
        )

        average_score = (
            sum(
                lead.commercial_score or 0
                for lead in leads
            ) / len(leads)
            if leads
            else 0
        )


        # ==========================================
        # SOURCE MONITORING — OPTIMIZED
        # ==========================================

        source_rows = (
            db.query(
                Lead.platform,

                func.count(
                    Lead.id
                ).label("total"),

                func.sum(
                    case(
                        (
                            Lead.commercial_score >= 40,
                            1
                        ),
                        else_=0
                    )
                ).label("actionable")
            )
            .filter(
                Lead.platform.isnot(None)
            )
            .group_by(
                Lead.platform
            )
            .order_by(
                func.count(Lead.id).desc()
            )
            .all()
        )

        source_stats = [
            {
                "name": platform,
                "total": total,
                "actionable": actionable or 0
            }
            for platform, total, actionable
            in source_rows
        ]


        # ==========================================
        # LEAD ANALYTICS
        # ==========================================

        analytics_actionable_rate = (
            (
                actionable_leads
                / total_stored_leads
            ) * 100
            if total_stored_leads
            else 0
        )

        analytics_data = {

            "total":
                total_stored_leads,

            "actionable":
                actionable_leads,

            "actionable_rate":
                round(
                    analytics_actionable_rate,
                    2
                ),

            "hot":
                analytics_hot,

            "warm":
                analytics_warm,

            "medium":
                analytics_medium,

            "low":
                analytics_low
        }


        # ==========================================
        # TEMPLATE RESPONSE
        # ==========================================

        response = templates.TemplateResponse(
            "index.html",
            {
                "request": request,

                "leads": leads,

                "total_stored_leads":
                    total_stored_leads,

                "actionable_leads":
                    actionable_leads,

                "hot_leads":
                    hot_leads,

                "warm_leads":
                    warm_leads,

                "medium_leads":
                    medium_leads,

                "production_sources":
                    production_sources,

                "best_score":
                    best_score,

                "average_score":
                    round(
                        average_score,
                        1
                    ),

                "source_stats":
                    source_stats,

                "analytics":
                    analytics_data
            }
        )

        return response

    finally:

        db.close()


@app.get("/search")
def search_leads(
    keyword: str = Query(""),
    platform: str = Query(""),
    priority: str = Query(""),
    service: str = Query(""),
    min_score: int = Query(0, ge=0, le=100)
):

    db = SessionLocal()

    try:

        query = db.query(Lead)

        # ==========================================
        # KEYWORD SEARCH
        # ==========================================

        if keyword.strip():

            search_term = f"%{keyword.strip()}%"

            query = query.filter(

                (Lead.title.ilike(search_term))
                |
                (Lead.description.ilike(search_term))
                |
                (Lead.primary_service.ilike(search_term))
                |
                (Lead.platform.ilike(search_term))

            )

        # ==========================================
        # PLATFORM FILTER
        # ==========================================

        if platform.strip():

            query = query.filter(
                Lead.platform == platform.strip()
            )

        # ==========================================
        # COMMERCIAL PRIORITY FILTER
        # ==========================================

        if priority.strip():

            query = query.filter(
                Lead.commercial_priority
                == priority.strip().upper()
            )

        # ==========================================
        # SERVICE FILTER
        # ==========================================

        if service.strip():

            query = query.filter(
                Lead.primary_service.ilike(
                    f"%{service.strip()}%"
                )
            )

        # ==========================================
        # MINIMUM COMMERCIAL SCORE
        # ==========================================

        query = query.filter(
            func.coalesce(
                Lead.commercial_score,
                0
            ) >= min_score
        )

        # ==========================================
        # BEST OPPORTUNITIES FIRST
        # ==========================================

        leads = (
            query
            .order_by(
                Lead.commercial_score.desc(),
                Lead.buyer_intent_score.desc(),
                Lead.business_fit_score.desc()
            )
            .limit(100)
            .all()
        )

        return {

            "count": len(leads),

            "results": [

                {
                    "id": lead.id,

                    "title": lead.title,

                    "platform": lead.platform,

                    "primary_service":
                        lead.primary_service,

                    "commercial_score":
                        lead.commercial_score or 0,

                    "commercial_priority":
                        lead.commercial_priority or "LOW",

                    "buyer_intent_score":
                        lead.buyer_intent_score or 0,

                    "business_fit_score":
                        lead.business_fit_score or 0,

                    "budget":
                        lead.budget or "Unknown",

                    "link":
                        lead.link or ""

                }

                for lead in leads
            ]
        }

    finally:

        db.close()

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request):

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request
        }
    )

@app.get("/filter")
def filter_leads(min_score: int = Query(0)):

    db = SessionLocal()

    leads = db.query(Lead).filter(
        Lead.lead_score >= min_score
    ).all()

    return [
        {
            "id": lead.id,
            "title": lead.title,
            "lead_score": lead.lead_score,
            "platform": lead.platform
        }
        for lead in leads
    ]

@app.get("/filter-platform")
def filter_platform(platform: str):

    db = SessionLocal()

    leads = db.query(Lead).filter(
        Lead.platform == platform
    ).all()

    return [
        {
            "id": lead.id,
            "title": lead.title,
            "lead_score": lead.lead_score,
            "platform": lead.platform
        }
        for lead in leads
    ]

@app.get("/export-csv")
def export_csv():

    db = SessionLocal()

    leads = db.query(Lead).all()

    filename = "leads_export.csv"

    with open(filename, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "Title",
            "Platform",
            "Business Type",
            "Budget",
            "Urgency",
            "Lead Score"
        ])

        for lead in leads:

            writer.writerow([
                lead.id,
                lead.title,
                lead.platform,
                lead.business_type,
                lead.budget,
                lead.urgency,
                lead.lead_score
            ])

    return FileResponse(
        path=filename,
        filename=filename,
        media_type="text/csv"
    )

@app.get("/sources")
def get_sources():

    db = SessionLocal()

    try:
        sources = db.query(Source).order_by(Source.name).all()

        return [
            {
                "id": source.id,
                "name": source.name,
                "category": source.category,
                "country": source.country,
                "enabled": source.enabled,
                "status": source.status,
                "last_run": source.last_run.isoformat() if source.last_run else None,
                "leads_collected": source.leads_collected,
            }
            for source in sources
        ]

    finally:
        db.close()

@app.post("/sources")
def create_source(source_data: SourceCreate):

    db = SessionLocal()

    try:

        # Check for duplicate source name
        existing = (
            db.query(Source)
            .filter(Source.name == source_data.name)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Source with this name already exists."
            )

        source = Source(
            name=source_data.name.strip(),
            category=source_data.category.strip(),
            country=source_data.country.strip(),
            enabled=source_data.enabled,
            status="Active" if source_data.enabled else "Disabled",
            leads_collected=0
        )

        db.add(source)
        db.commit()
        db.refresh(source)

        return {
            "id": source.id,
            "name": source.name,
            "category": source.category,
            "country": source.country,
            "enabled": source.enabled,
            "status": source.status,
            "last_run": (
                source.last_run.isoformat()
                if source.last_run
                else None
            ),
            "leads_collected": source.leads_collected
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to create source: {str(e)}"
        )

    finally:

        db.close()

@app.put("/sources/{source_id}")
def update_source(source_id: int, update: SourceUpdate):

    db = SessionLocal()

    try:

        source = (
            db.query(Source)
            .filter(Source.id == source_id)
            .first()
        )

        if not source:
            raise HTTPException(
                status_code=404,
                detail="Source not found"
            )

        # Update enabled state
        source.enabled = update.enabled

        # Keep status synchronized
        source.status = (
            "Active"
            if update.enabled
            else "Disabled"
        )

        db.commit()

        db.refresh(source)

        return {
            "message": "Source updated successfully",
            "source": {
                "id": source.id,
                "name": source.name,
                "enabled": source.enabled,
                "status": source.status
            }
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to update source: {str(e)}"
        )

    finally:

        db.close()

@app.post("/scrape")
def scrape():

    return run_enabled_scrapers()

@app.get("/dashboard/summary")
def dashboard_summary():

    db = SessionLocal()

    try:

        # =====================================================
        # TOTAL STORED LEADS
        # =====================================================

        total_leads = db.query(Lead).count()


        # =====================================================
        # NEW CRM LEADS
        # =====================================================

        new_leads = (
            db.query(Lead)
            .filter(Lead.crm_status == "New")
            .count()
        )


        # =====================================================
        # ACTIONABLE COMMERCIAL OPPORTUNITIES
        # commercial_score >= 40
        # =====================================================

        actionable_leads = (
            db.query(Lead)
            .filter(Lead.commercial_score >= 40)
            .count()
        )


        # =====================================================
        # AVERAGE COMMERCIAL SCORE
        # =====================================================

        average_commercial_score = (
            db.query(
                func.avg(Lead.commercial_score)
            )
            .scalar()
        )

        if average_commercial_score is None:
            average_commercial_score = 0


        # =====================================================
        # BEST COMMERCIAL SCORE
        # =====================================================

        best_commercial_score = (
            db.query(
                func.max(Lead.commercial_score)
            )
            .scalar()
        )

        if best_commercial_score is None:
            best_commercial_score = 0


        # =====================================================
        # DATA SOURCES
        # Distinct platforms represented in stored leads
        # =====================================================

        data_sources = (
            db.query(
                func.count(
                    func.distinct(Lead.platform)
                )
            )
            .filter(
                Lead.platform.isnot(None),
                Lead.platform != ""
            )
            .scalar()
        ) or 0


        # =====================================================
        # ENABLED SCRAPER SOURCES
        # =====================================================

        active_sources = (
            db.query(Source)
            .filter(Source.enabled == True)
            .count()
        )


        # =====================================================
        # PRIORITY COUNTS
        # =====================================================

        priority_rows = (
            db.query(
                Lead.commercial_priority,
                func.count(Lead.id)
            )
            .group_by(
                Lead.commercial_priority
            )
            .all()
        )

        priority_distribution = {
            "HOT": 0,
            "WARM": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        for priority, count in priority_rows:

            if priority in priority_distribution:
                priority_distribution[priority] = count


        # =====================================================
        # RESPONSE
        # =====================================================

        return {
            "total_leads": total_leads,
            "new_leads": new_leads,
            "actionable_leads": actionable_leads,

            "average_commercial_score": round(
                float(average_commercial_score),
                2
            ),

            "best_commercial_score": round(
                float(best_commercial_score),
                2
            ),

            "data_sources": data_sources,
            "active_sources": active_sources,

            "priority_distribution": priority_distribution
        }

    finally:

        db.close()


@app.get("/dashboard/analytics")
def dashboard_analytics():

    db = SessionLocal()

    try:

        # =====================================================
        # CANONICAL ANALYTICS DATASET
        # =====================================================
        # All analytics below are calculated from the same
        # Lead table used by the rest of the application.

        total_leads = (
            db.query(Lead)
            .count()
        )

        # =====================================================
        # AVERAGE SCORE
        # =====================================================

        average_score = (
            db.query(
                func.avg(Lead.lead_score)
            )
            .filter(
                Lead.lead_score.isnot(None)
            )
            .scalar()
        )

        # =====================================================
        # HIGH SCORE LEADS
        # Score >= 80
        # =====================================================

        high_score_leads = (
            db.query(Lead)
            .filter(
                Lead.lead_score >= 80
            )
            .count()
        )

        # =====================================================
        # ACTIVE PLATFORMS
        # =====================================================

        active_platforms = (
            db.query(
                Lead.platform
            )
            .filter(
                Lead.platform.isnot(None),
                Lead.platform != ""
            )
            .distinct()
            .count()
        )

        # =====================================================
        # LEADS BY PLATFORM
        # =====================================================

        platform_rows = (
            db.query(
                Lead.platform,
                func.count(Lead.id)
            )
            .filter(
                Lead.platform.isnot(None),
                Lead.platform != ""
            )
            .group_by(
                Lead.platform
            )
            .order_by(
                func.count(Lead.id).desc()
            )
            .all()
        )

        leads_by_platform = [
            {
                "name": platform,
                "value": count
            }
            for platform, count in platform_rows
        ]

        # =====================================================
        # SCORE DISTRIBUTION
        # =====================================================

        score_distribution = [
            {
                "range": "90+",
                "count": (
                    db.query(Lead)
                    .filter(
                        Lead.lead_score >= 90
                    )
                    .count()
                )
            },
            {
                "range": "80-89",
                "count": (
                    db.query(Lead)
                    .filter(
                        Lead.lead_score >= 80,
                        Lead.lead_score < 90
                    )
                    .count()
                )
            },
            {
                "range": "70-79",
                "count": (
                    db.query(Lead)
                    .filter(
                        Lead.lead_score >= 70,
                        Lead.lead_score < 80
                    )
                    .count()
                )
            },
            {
                "range": "<70",
                "count": (
                    db.query(Lead)
                    .filter(
                        Lead.lead_score < 70
                    )
                    .count()
                )
            }
        ]

        # =====================================================
        # STATUS DISTRIBUTION
        # =====================================================

        status_rows = (
            db.query(
                Lead.crm_status,
                func.count(Lead.id)
            )
            .group_by(
                Lead.crm_status
            )
            .all()
        )

        status_distribution = [
            {
                "name": status or "Unknown",
                "value": count
            }
            for status, count in status_rows
        ]

        # =====================================================
        # EXISTING ACTIONABLE OPPORTUNITIES
        # =====================================================

        actionable_leads = (
            db.query(Lead)
            .filter(
                Lead.commercial_score >= 40
            )
            .count()
        )

        actionable_rate = (
            (actionable_leads / total_leads) * 100
            if total_leads
            else 0
        )

        # =====================================================
        # EXISTING PRIORITY DISTRIBUTION
        # =====================================================

        priority_distribution = {
            "HOT": 0,
            "WARM": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        priority_rows = (
            db.query(
                Lead.commercial_priority,
                func.count(Lead.id)
            )
            .filter(
                Lead.commercial_priority.isnot(None)
            )
            .group_by(
                Lead.commercial_priority
            )
            .all()
        )

        for priority, count in priority_rows:

            if priority in priority_distribution:
                priority_distribution[priority] = count

        # =====================================================
        # EXISTING SOURCE PERFORMANCE
        # =====================================================

        source_rows = (
            db.query(
                Lead.platform,
                func.count(Lead.id)
            )
            .filter(
                Lead.platform.isnot(None),
                Lead.platform != ""
            )
            .group_by(
                Lead.platform
            )
            .order_by(
                func.count(Lead.id).desc()
            )
            .all()
        )

        source_performance = []

        for platform, total in source_rows:

            actionable = (
                db.query(Lead)
                .filter(
                    Lead.platform == platform,
                    Lead.commercial_score >= 40
                )
                .count()
            )

            conversion_rate = (
                (actionable / total) * 100
                if total
                else 0
            )

            source_performance.append({
                "platform": platform,
                "total": total,
                "actionable": actionable,
                "conversion_rate": round(
                    conversion_rate,
                    2
                )
            })

        # =====================================================
        # EXISTING SERVICE DISTRIBUTION
        # =====================================================

        service_rows = (
            db.query(
                Lead.primary_service,
                func.count(Lead.id)
            )
            .filter(
                Lead.primary_service.isnot(None),
                Lead.primary_service != ""
            )
            .group_by(
                Lead.primary_service
            )
            .order_by(
                func.count(Lead.id).desc()
            )
            .all()
        )

        service_distribution = [
            {
                "service": service,
                "count": count
            }
            for service, count in service_rows
        ]

        # =====================================================
        # EXISTING COMMERCIAL SCORE STATISTICS
        # =====================================================

        average_commercial_score = (
            db.query(
                func.avg(
                    Lead.commercial_score
                )
            )
            .filter(
                Lead.commercial_score.isnot(None)
            )
            .scalar()
        )

        best_commercial_score = (
            db.query(
                func.max(
                    Lead.commercial_score
                )
            )
            .scalar()
        )

        # =====================================================
        # FINAL ANALYTICS RESPONSE
        # =====================================================

        return {

            # Day 5 Analytics
            "total_leads": total_leads,

            "average_score": round(
                float(
                    average_score or 0
                ),
                2
            ),

            "high_score_leads": high_score_leads,

            "active_platforms": active_platforms,

            "leads_by_platform": leads_by_platform,

            "score_distribution": score_distribution,

            "status_distribution": status_distribution,

            # Existing Analytics
            "actionable_leads": actionable_leads,

            "actionable_rate": round(
                actionable_rate,
                2
            ),

            "average_commercial_score": round(
                float(
                    average_commercial_score or 0
                ),
                2
            ),

            "best_commercial_score":
                best_commercial_score or 0,

            "priority_distribution":
                priority_distribution,

            "source_performance":
                source_performance,

            "service_distribution":
                service_distribution
        }

    finally:

        db.close()

@app.post("/lead/{lead_id}/status")
def update_lead_status(
    lead_id: int,
    crm_status: str = Form(...),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        return {"success": False, "message": "Lead not found"}

    if (
        crm_status == "Contacted"
        and lead.opportunity_status in {
            "CLOSED",
            "EXPIRED",
            "REMOVED"
        }
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot contact a "
                f"{lead.opportunity_status} opportunity."
            )
        )

    lead.crm_status = crm_status

    if crm_status == "Contacted":
        lead.last_contact_date = datetime.utcnow()
        lead.meeting_scheduled = False
        lead.proposal_sent = False
        lead.won = False
        lead.lost = False

    elif crm_status == "Meeting Scheduled":
        lead.meeting_scheduled = True
        lead.proposal_sent = False
        lead.won = False
        lead.lost = False

    elif crm_status == "Proposal Sent":
        lead.proposal_sent = True
        lead.meeting_scheduled = False
        lead.won = False
        lead.lost = False

    elif crm_status == "Won":
        lead.won = True
        lead.lost = False
        lead.meeting_scheduled = False
        lead.proposal_sent = False

    elif crm_status == "Lost":
        lead.lost = True
        lead.won = False
        lead.meeting_scheduled = False
        lead.proposal_sent = False

    else:
        lead.meeting_scheduled = False
        lead.proposal_sent = False
        lead.won = False
        lead.lost = False

    db.commit()

    return {
        "success": True,
        "status": crm_status
    }

@app.patch("/lead/{lead_id}/crm-state")
def update_crm_state(
    lead_id: int,
    update: CRMStateUpdate,
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    # ---------------------------------------------------------
    # PROPOSAL SENT
    # ---------------------------------------------------------
    if update.proposal_sent is not None:
        lead.proposal_sent = update.proposal_sent

        if update.proposal_sent:
            # Keep existing CRM vocabulary.
            # Proposal Sent is a valid sales stage.
            lead.crm_status = "Proposal Sent"

        elif lead.crm_status == "Proposal Sent":
            # Move back to the most reasonable active stage.
            if lead.meeting_scheduled:
                lead.crm_status = "Meeting Scheduled"
            else:
                lead.crm_status = "Contacted"

    # ---------------------------------------------------------
    # MEETING SCHEDULED
    # ---------------------------------------------------------
    if update.meeting_scheduled is not None:
        lead.meeting_scheduled = update.meeting_scheduled

        if update.meeting_scheduled:
            lead.crm_status = "Meeting Scheduled"

        elif lead.crm_status == "Meeting Scheduled":
            if lead.proposal_sent:
                lead.crm_status = "Proposal Sent"
            else:
                lead.crm_status = "Contacted"

    # ---------------------------------------------------------
    # OUTCOME
    # ---------------------------------------------------------
    if update.outcome is not None:

        allowed_outcomes = {
            "Open",
            "Won",
            "Lost"
        }

        if update.outcome not in allowed_outcomes:
            raise HTTPException(
                status_code=400,
                detail="Invalid outcome. Use Open, Won, or Lost."
            )

        if update.outcome == "Won":
            lead.won = True
            lead.lost = False
            lead.crm_status = "Won"

        elif update.outcome == "Lost":
            lead.won = False
            lead.lost = True
            lead.crm_status = "Lost"

        else:
            # Open
            lead.won = False
            lead.lost = False

            # Restore an active CRM stage.
            if lead.proposal_sent:
                lead.crm_status = "Proposal Sent"
            elif lead.meeting_scheduled:
                lead.crm_status = "Meeting Scheduled"
            else:
                lead.crm_status = "Contacted"

    db.commit()
    db.refresh(lead)

    return {
        "success": True,
        "lead": {
            "id": lead.id,
            "crm_status": lead.crm_status,
            "proposal_sent": lead.proposal_sent,
            "meeting_scheduled": lead.meeting_scheduled,
            "won": lead.won,
            "lost": lead.lost
        }
    }

@app.post("/lead/{lead_id}/notes")
def update_notes(
    lead_id: int,
    notes: str = Form(...),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        return {"success": False}

    lead.notes = notes

    db.commit()

    return {
        "success": True
    }

@app.post("/lead/{lead_id}/followup")
def update_followup(
    lead_id: int,
    next_followup: str = Form(...),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        return {"success": False}

    lead.next_followup = datetime.fromisoformat(next_followup)

    db.commit()

    return {
        "success": True
    }

@app.post("/lead/{lead_id}/deal-value")
def update_deal_value(
    lead_id: int,
    deal_value: float = Form(...),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        return {
            "success": False,
            "message": "Lead not found"
        }

    lead.deal_value = deal_value

    db.commit()
    db.refresh(lead)

    return {
        "success": True,
        "deal_value": lead.deal_value
    }

@app.post("/lead/{lead_id}/assign")
def assign_lead(
    lead_id: int,
    assigned_to: str = Form(...),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        return {"success": False}

    lead.assigned_to = assigned_to

    db.commit()

    return {
        "success": True
    }

@app.post("/lead/{lead_id}/company")
def update_company_information(
    lead_id: int,
    company_name: str = Form(""),
    industry: str = Form(""),
    country: str = Form(""),
    website: str = Form(""),
    email: str = Form(""),
    linkedin: str = Form(""),
    twitter: str = Form(""),
    db: Session = Depends(get_db)
):

    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        return {
            "success": False,
            "message": "Lead not found"
        }

    lead.company_name = company_name.strip()
    lead.industry = industry.strip()
    lead.country = country.strip()
    lead.website = website.strip()
    lead.email = email.strip()
    lead.linkedin = linkedin.strip()
    lead.twitter = twitter.strip()

    db.commit()
    db.refresh(lead)

    return {
        "success": True,
        "company_name": lead.company_name,
        "industry": lead.industry,
        "country": lead.country,
        "website": lead.website,
        "email": lead.email,
        "linkedin": lead.linkedin,
        "twitter": lead.twitter
    }

@app.get("/crm-summary")
def crm_summary(db: Session = Depends(get_db)):

    return {
        "new": db.query(Lead).filter(Lead.crm_status == "New").count(),
        "viewed": db.query(Lead).filter(Lead.crm_status == "Viewed").count(),
        "contacted": db.query(Lead).filter(Lead.crm_status == "Contacted").count(),
        "meeting": db.query(Lead).filter(Lead.crm_status == "Meeting Scheduled").count(),
        "proposal": db.query(Lead).filter(Lead.crm_status == "Proposal Sent").count(),
        "negotiation": db.query(Lead).filter(Lead.crm_status == "Negotiation").count(),
        "won": db.query(Lead).filter(Lead.crm_status == "Won").count(),
        "lost": db.query(Lead).filter(Lead.crm_status == "Lost").count()
    }

@app.get("/lead-details/{lead_id}", response_class=HTMLResponse)
def lead_details(request: Request, lead_id: int):

    db = SessionLocal()

    try:

        lead = (
            db.query(Lead)
            .filter(Lead.id == lead_id)
            .first()
        )

        if not lead:
            raise HTTPException(
                status_code=404,
                detail="Lead not found"
            )

        return templates.TemplateResponse(
            "lead_details.html",
            {
                "request": request,
                "lead": lead
            }
        )

    finally:
        db.close()

@app.get("/crm-dashboard", response_class=HTMLResponse)
def crm_dashboard(request: Request):

    db = SessionLocal()

    crm_data = {
        "new": db.query(Lead).filter(Lead.crm_status == "New").all(),
        "viewed": db.query(Lead).filter(Lead.crm_status == "Viewed").all(),
        "contacted": db.query(Lead).filter(Lead.crm_status == "Contacted").all(),
        "meeting": db.query(Lead).filter(Lead.crm_status == "Meeting Scheduled").all(),
        "proposal": db.query(Lead).filter(Lead.crm_status == "Proposal Sent").all(),
        "negotiation": db.query(Lead).filter(Lead.crm_status == "Negotiation").all(),
        "won": db.query(Lead).filter(Lead.crm_status == "Won").all(),
        "lost": db.query(Lead).filter(Lead.crm_status == "Lost").all(),
    }

    reminders = {

        "overdue": len(
            db.query(Lead).filter(
                Lead.next_followup != None,
                Lead.next_followup < datetime.now()
            ).all()
        ),

        "today": 0,

        "hot": db.query(Lead).filter(
            Lead.commercial_priority == "HOT",
            Lead.crm_status != "Contacted"
        ).count(),

        "proposal": db.query(Lead).filter(
            Lead.crm_status == "Proposal Sent"
        ).count(),

        "new": db.query(Lead).filter(
            Lead.crm_status == "New"
        ).count()

    }

    return templates.TemplateResponse(

        "crm_dashboard.html",

        {

            "request": request,

            "crm": crm_data,

            "reminders": reminders

        }

    )

@app.get("/crm-analytics")
def crm_analytics():

    db = SessionLocal()

    total = db.query(Lead).count()

    won = db.query(Lead).filter(
        Lead.crm_status == "Won"
    ).count()

    lost = db.query(Lead).filter(
        Lead.crm_status == "Lost"
    ).count()

    proposal = db.query(Lead).filter(
        Lead.crm_status == "Proposal Sent"
    ).count()

    meeting = db.query(Lead).filter(
        Lead.crm_status == "Meeting Scheduled"
    ).count()

    contacted = db.query(Lead).filter(
        Lead.crm_status == "Contacted"
    ).count()

    overdue = db.query(Lead).filter(
        Lead.next_followup != None,
        Lead.next_followup < datetime.utcnow()
    ).count()

    conversion_rate = 0

    if total > 0:
        conversion_rate = round((won / total) * 100, 2)

    return {

        "total_leads": total,

        "contacted": contacted,

        "meetings": meeting,

        "proposals": proposal,

        "won": won,

        "lost": lost,

        "overdue_followups": overdue,

        "conversion_rate": conversion_rate

    }

@app.get("/crm-analytics-dashboard", response_class=HTMLResponse)
def crm_analytics_dashboard(request: Request):

    db = SessionLocal()

    analytics = {

        "total": db.query(Lead).count(),

        "won": db.query(Lead).filter(
            Lead.crm_status == "Won"
        ).count(),

        "lost": db.query(Lead).filter(
            Lead.crm_status == "Lost"
        ).count(),

        "contacted": db.query(Lead).filter(
            Lead.crm_status == "Contacted"
        ).count(),

        "proposal": db.query(Lead).filter(
            Lead.crm_status == "Proposal Sent"
        ).count(),

        "meeting": db.query(Lead).filter(
            Lead.crm_status == "Meeting Scheduled"
        ).count()

    }

    return templates.TemplateResponse(

        "crm_analytics.html",

        {

            "request": request,

            "analytics": analytics

        }

    )

@app.get("/crm-reminders")
def crm_reminders():

    db = SessionLocal()

    today = date.today()

    overdue = db.query(Lead).filter(
        Lead.next_followup != None,
        Lead.next_followup < datetime.now()
    ).all()

    today_followups = db.query(Lead).filter(
        Lead.next_followup != None
    ).all()

    today_followups = [
        lead for lead in today_followups
        if lead.next_followup.date() == today
    ]

    new_leads = db.query(Lead).filter(
        Lead.crm_status == "New"
    ).all()

    hot_leads = db.query(Lead).filter(
        Lead.commercial_priority == "HOT",
        Lead.crm_status != "Contacted"
    ).all()

    pending_proposals = db.query(Lead).filter(
        Lead.crm_status == "Proposal Sent"
    ).all()

    return {

        "overdue": len(overdue),

        "today": len(today_followups),

        "new": len(new_leads),

        "hot": len(hot_leads),

        "proposal": len(pending_proposals)

    }

@app.post("/lead/{lead_id}/generate-outreach")
def generate_lead_outreach(
    lead_id: int,
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    if lead.opportunity_status in {
        "CLOSED",
        "EXPIRED",
        "REMOVED"
    }:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot generate outreach for a "
                f"{lead.opportunity_status} opportunity."
            )
        )

    lead_data = {
        "title": lead.title,
        "description": lead.description,
        "business_type": lead.business_type,
        "service_needed": lead.service_needed,
        "technology": lead.technology,
        "company_name": lead.company_name,
        "industry": lead.industry,
        "country": lead.country,
        "website": lead.website,
        "budget": lead.budget,
        "urgency": lead.urgency,
        "buyer_intent_score": lead.buyer_intent_score,
        "business_fit_score": lead.business_fit_score,
        "commercial_score": lead.commercial_score,
        "commercial_priority": lead.commercial_priority,
        "ranking_reason": lead.ranking_reason
    }

    result = generate_outreach(lead_data)

    lead.outreach_strategy = result.get(
        "strategy",
        ""
    )

    lead.outreach_message = json.dumps({
        "subject": result.get(
            "subject",
            "Project Discussion"
        ),
        "message": result.get(
            "message",
            ""
        )
    })

    db.commit()
    db.refresh(lead)

    return {
        "success": True,
        "strategy": lead.outreach_strategy,
        "subject": result.get("subject"),
        "message": result.get("message")
    }

@app.post("/lead/{lead_id}/outreach")
def save_lead_outreach(
    lead_id: int,
    subject: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    outreach_data = {
        "subject": subject.strip(),
        "message": message.strip()
    }

    lead.outreach_message = json.dumps(outreach_data)

    db.commit()
    db.refresh(lead)

    return {
        "success": True,
        "subject": outreach_data["subject"],
        "message": outreach_data["message"]
    }

# ============================================================
# NOTIFICATION SETTINGS
# ============================================================

class NotificationSettings(BaseModel):

    hotLead: bool = True
    pipelineCompleted: bool = True
    pipelineFailed: bool = True


@app.get("/notification-settings")
def get_notification_settings_api():

    from notifications.notifier import (
        get_notification_settings
    )

    return get_notification_settings()


@app.put("/notification-settings")
def update_notification_settings_api(
    settings: NotificationSettings
):

    from notifications.notifier import (
        save_notification_settings
    )

    updated = save_notification_settings(
        settings.model_dump()
    )

    return {
        "success": True,
        "settings": updated
    }
