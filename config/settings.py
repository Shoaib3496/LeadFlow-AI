import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# Application Environment
# ==========================

APP_ENV = os.getenv(
    "APP_ENV",
    "development"
).strip().lower()

VALID_ENVIRONMENTS = {
    "development",
    "production",
    "testing"
}

if APP_ENV not in VALID_ENVIRONMENTS:
    raise ValueError(
        f"Invalid APP_ENV '{APP_ENV}'. "
        f"Expected one of: "
        f"{', '.join(sorted(VALID_ENVIRONMENTS))}"
    )

IS_DEVELOPMENT = APP_ENV == "development"
IS_PRODUCTION = APP_ENV == "production"
IS_TESTING = APP_ENV == "testing"

# ==========================
# API / Server
# ==========================

API_HOST = os.getenv(
    "API_HOST",
    "127.0.0.1"
)

API_PORT = int(
    os.getenv(
        "API_PORT",
        "8000"
    )
)

API_RELOAD = os.getenv(
    "API_RELOAD",
    "true"
).strip().lower() in {
    "1",
    "true",
    "yes",
    "on"
}


# ==========================
# CORS
# ==========================

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173"
    ).split(",")
    if origin.strip()
]

# ==========================
# AI
# ==========================

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# ==========================
# Database
# ==========================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DEFAULT_DATABASE_PATH = os.path.join(
    PROJECT_ROOT,
    "database",
    "leadflow.db"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DEFAULT_DATABASE_PATH}"
)

# Product Hunt
PRODUCTHUNT_API_KEY = os.getenv("PRODUCTHUNT_API_KEY")
PRODUCTHUNT_API_SECRET = os.getenv("PRODUCTHUNT_API_SECRET")

# ==========================
# Notifications
# ==========================

ENABLE_NOTIFICATIONS = True

# ==========================
# Duplicate Detection
# ==========================

SIMILARITY_THRESHOLD = 0.90

# ==========================
# Lead Scoring
# ==========================

HIGH_SCORE = 70
MEDIUM_SCORE = 40
LOW_SCORE = 40

# ==========================
# Scheduler
# ==========================

SCHEDULER_INTERVAL_MINUTES = 10

# ==========================
# Hacker News
# ==========================

HN_LIMIT = 20

# ==========================
# Product Hunt
# ==========================

PRODUCTHUNT_ACCESS_TOKEN = os.getenv(
    "PRODUCTHUNT_ACCESS_TOKEN",
    ""
)

# ==========================
# Reddit
# ==========================

REDDIT_CLIENT_ID = os.getenv(
    "REDDIT_CLIENT_ID",
    ""
)

REDDIT_CLIENT_SECRET = os.getenv(
    "REDDIT_CLIENT_SECRET",
    ""
)

REDDIT_USER_AGENT = os.getenv(
    "REDDIT_USER_AGENT",
    "LeadFlowAI/1.0"
)