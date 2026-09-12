"""
LeadFlow AI - Universal Opportunity Status

Converts platform-specific status information into
a common LeadFlow opportunity status.

Universal statuses:
    OPEN
    CLOSED
    EXPIRED
    REMOVED
    UNKNOWN
"""

from datetime import datetime, timezone
from typing import Any, Dict


# ============================================================
# UNIVERSAL STATUS VALUES
# ============================================================

OPEN = "OPEN"
CLOSED = "CLOSED"
EXPIRED = "EXPIRED"
REMOVED = "REMOVED"
UNKNOWN = "UNKNOWN"


VALID_STATUSES = {
    OPEN,
    CLOSED,
    EXPIRED,
    REMOVED,
    UNKNOWN,
}


# ============================================================
# STATUS RESULT
# ============================================================

def status_result(
    opportunity_status: str,
    source_status: str = "",
) -> Dict[str, Any]:
    """
    Return a standardized opportunity-status result.
    """

    if opportunity_status not in VALID_STATUSES:
        opportunity_status = UNKNOWN

    return {
        "opportunity_status": opportunity_status,
        "source_status": source_status or "",
        "freshness_checked_at": datetime.now(timezone.utc),
    }


# ============================================================
# GENERIC STATUS NORMALIZATION
# ============================================================

def normalize_status(value: Any) -> str:
    """
    Normalize a raw platform status into LeadFlow's
    universal status vocabulary.

    This function only handles explicit status values.
    It does NOT guess whether an opportunity is open
    based on unrelated text.
    """

    if value is None:
        return UNKNOWN

    value = str(value).strip().lower()

    if not value:
        return UNKNOWN

    # -----------------------------
    # Explicit OPEN states
    # -----------------------------

    if value in {
        "open",
        "active",
        "opened",
        "available",
        "published",
        "live",
        "hiring",
    }:
        return OPEN

    # -----------------------------
    # Explicit CLOSED states
    # -----------------------------

    if value in {
        "closed",
        "close",
        "complete",
        "completed",
        "awarded",
        "finished",
        "inactive",
    }:
        return CLOSED

    # -----------------------------
    # Explicit EXPIRED states
    # -----------------------------

    if value in {
        "expired",
        "expire",
        "deadline_passed",
    }:
        return EXPIRED

    # -----------------------------
    # Explicit REMOVED states
    # -----------------------------

    if value in {
        "removed",
        "deleted",
        "not_found",
        "404",
    }:
        return REMOVED

    return UNKNOWN


# ============================================================
# FREELANCER
# ============================================================

def freelancer_status(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine Freelancer opportunity status.

    Freelancer provides explicit project status information,
    so we use that information instead of guessing.
    """

    if raw_data.get("deleted") is True:
        return status_result(
            REMOVED,
            "deleted",
        )

    raw_status = raw_data.get(
        "frontend_project_status"
    )

    if raw_status is None:
        raw_status = raw_data.get("status")

    normalized = normalize_status(raw_status)

    return status_result(
        normalized,
        str(raw_status or ""),
    )

def freelancer_detail_status(project_data):
    """
    Determine the current status of a Freelancer project
    from the project-detail API response.
    """

    if not project_data:
        return status_result(UNKNOWN)

    if project_data.get("deleted"):
        return status_result(
            REMOVED,
            "deleted"
        )

    frontend_status = (
        project_data.get(
            "frontend_project_status"
        )
        or ""
    ).strip().lower()

    if frontend_status:
        return status_result(
            normalize_status(frontend_status),
            frontend_status
        )

    project_status = (
        project_data.get(
            "status"
        )
        or ""
    ).strip().lower()

    if project_status:
        return status_result(
            normalize_status(project_status),
            project_status
        )

    return status_result(UNKNOWN)


# ============================================================
# REMOTEOK
# ============================================================

def remoteok_status(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine RemoteOK opportunity status.

    Only explicit job status information is used.
    """

    raw_status = (
        raw_data.get("status")
        or raw_data.get("job_status")
        or raw_data.get("state")
    )

    normalized = normalize_status(raw_status)

    return status_result(
        normalized,
        str(raw_status or ""),
    )


# ============================================================
# GITHUB
# ============================================================

def github_status(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine GitHub opportunity status.

    GitHub issues/requests do not always represent a
    traditional commercial job opportunity.

    Therefore we only mark the opportunity CLOSED when
    GitHub explicitly reports a closed state.

    Otherwise we keep it UNKNOWN rather than incorrectly
    claiming that an issue is open.
    """

    raw_status = (
        raw_data.get("state")
        or raw_data.get("status")
    )

    if raw_status is None:
        return status_result(
            UNKNOWN,
            "",
        )

    normalized = normalize_status(raw_status)

    if normalized == OPEN:
        return status_result(
            OPEN,
            str(raw_status),
        )

    if normalized == CLOSED:
        return status_result(
            CLOSED,
            str(raw_status),
        )

    return status_result(
        UNKNOWN,
        str(raw_status),
    )


# ============================================================
# HACKER NEWS
# ============================================================

def hacker_news_status(
    raw_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Hacker News posts do not have a reliable commercial
    opportunity open/closed lifecycle.

    Therefore we do not infer OPEN/CLOSED from the post
    merely existing.

    Explicit removal/deletion signals are still respected.
    """

    if raw_data.get("deleted") is True:
        return status_result(
            REMOVED,
            "deleted",
        )

    return status_result(
        UNKNOWN,
        "",
    )


# ============================================================
# DEV.TO
# ============================================================

def devto_status(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dev.to articles/posts do not have a normal commercial
    opportunity lifecycle.

    Do not mark them OPEN simply because the article exists.
    """

    if raw_data.get("deleted") is True:
        return status_result(
            REMOVED,
            "deleted",
        )

    return status_result(
        UNKNOWN,
        "",
    )


# ============================================================
# PRODUCT HUNT
# ============================================================

def product_hunt_status(
    raw_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Product Hunt products are not automatically commercial
    job opportunities.

    Only explicit lifecycle status is used.
    """

    raw_status = (
        raw_data.get("status")
        or raw_data.get("state")
    )

    if raw_status:
        normalized = normalize_status(raw_status)

        return status_result(
            normalized,
            str(raw_status),
        )

    return status_result(
        UNKNOWN,
        "",
    )


# ============================================================
# RSS
# ============================================================

def rss_status(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    RSS content normally has no explicit opportunity
    lifecycle.

    Therefore RSS items remain UNKNOWN unless the source
    explicitly provides a usable status.
    """

    raw_status = raw_data.get(
        "status"
    )

    if raw_status:
        normalized = normalize_status(raw_status)

        return status_result(
            normalized,
            str(raw_status),
        )

    return status_result(
        UNKNOWN,
        "",
    )


# ============================================================
# UNIVERSAL PLATFORM DISPATCHER
# ============================================================

def determine_opportunity_status(
    platform: str,
    raw_data: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Universal entry point.

    Parameters
    ----------
    platform:
        Platform/source name.

    raw_data:
        Raw scraper data.

    Returns
    -------
    dict:
        opportunity_status
        source_status
        freshness_checked_at
    """

    raw_data = raw_data or {}

    platform_key = (
        str(platform or "")
        .strip()
        .lower()
    )

    # Freelancer
    if platform_key == "freelancer":
        return freelancer_status(raw_data)

    # RemoteOK
    if platform_key == "remoteok":
        return remoteok_status(raw_data)

    # GitHub
    if platform_key == "github":
        return github_status(raw_data)

    # Hacker News
    if platform_key in {
        "hacker news",
        "hacker news rss",
        "hackernews",
    }:
        return hacker_news_status(raw_data)

    # Dev.to
    if platform_key == "dev.to":
        return devto_status(raw_data)

    # Product Hunt
    if platform_key == "product hunt":
        return product_hunt_status(raw_data)

    # RSS
    if platform_key == "rss":
        return rss_status(raw_data)

    # Unknown source
    return status_result(
        UNKNOWN,
        "",
    )