
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from config.settings import (
    APP_ENV,
    IS_PRODUCTION,
    DATABASE_URL,
    API_HOST,
    API_PORT,
    API_RELOAD,
    CORS_ORIGINS,
    OLLAMA_MODEL,
    PRODUCTHUNT_API_KEY,
    PRODUCTHUNT_API_SECRET,
    PRODUCTHUNT_ACCESS_TOKEN,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
)


class ConfigurationValidator:

    VALID_ENVIRONMENTS = {
        "development",
        "production",
        "testing",
    }

    def __init__(self):

        self.errors = []
        self.warnings = []

    # =====================================================
    # ERROR / WARNING HELPERS
    # =====================================================

    def add_error(self, message):

        self.errors.append(message)

    def add_warning(self, message):

        self.warnings.append(message)

    # =====================================================
    # APPLICATION ENVIRONMENT
    # =====================================================

    def validate_environment(self):

        if APP_ENV not in self.VALID_ENVIRONMENTS:

            self.add_error(
                f"Invalid APP_ENV: {APP_ENV}"
            )

    # =====================================================
    # API
    # =====================================================

    def validate_api(self):

        if not API_HOST:

            self.add_error(
                "API_HOST cannot be empty."
            )

        if not isinstance(API_PORT, int):

            self.add_error(
                "API_PORT must be an integer."
            )

        elif not 1 <= API_PORT <= 65535:

            self.add_error(
                "API_PORT must be between 1 and 65535."
            )

    # =====================================================
    # DATABASE
    # =====================================================

    def validate_database(self):

        if not DATABASE_URL:

            self.add_error(
                "DATABASE_URL cannot be empty."
            )

            return

        try:

            database_url = make_url(
                DATABASE_URL
            )

            if not database_url.drivername:

                self.add_error(
                    "DATABASE_URL has no database driver."
                )

        except ArgumentError as exc:

            self.add_error(
                f"Invalid DATABASE_URL: {exc}"
            )

    # =====================================================
    # CORS
    # =====================================================

    def validate_cors(self):

        if not CORS_ORIGINS:

            self.add_warning(
                "No CORS origins configured."
            )

        for origin in CORS_ORIGINS:

            if not (
                origin.startswith("http://")
                or
                origin.startswith("https://")
            ):

                self.add_error(
                    f"Invalid CORS origin: {origin}"
                )

    # =====================================================
    # AI
    # =====================================================

    def validate_ai(self):

        if not OLLAMA_MODEL or not OLLAMA_MODEL.strip():

            self.add_error(
                "OLLAMA_MODEL cannot be empty."
            )

    # =====================================================
    # HELPER
    # =====================================================

    @staticmethod
    def has_value(value):

        return bool(
            value
            and
            str(value).strip()
        )

    def validate_optional_services(self):

    # =====================================================
    # PRODUCT HUNT
    # =====================================================

        producthunt_key = self.has_value(
            PRODUCTHUNT_API_KEY
        )

        producthunt_secret = self.has_value(
            PRODUCTHUNT_API_SECRET
        )

        producthunt_token = self.has_value(
            PRODUCTHUNT_ACCESS_TOKEN
        )

        if producthunt_key and not producthunt_secret:

            self.add_warning(
                "PRODUCTHUNT_API_KEY exists but "
                "PRODUCTHUNT_API_SECRET is missing."
            )

        if producthunt_secret and not producthunt_key:

            self.add_warning(
                "PRODUCTHUNT_API_SECRET exists but "
                "PRODUCTHUNT_API_KEY is missing."
            )

        # Access token may be used independently.
        # Therefore its absence is not an error.


        # =====================================================
        # REDDIT
        # =====================================================

        reddit_client_id = self.has_value(
            REDDIT_CLIENT_ID
        )

        reddit_client_secret = self.has_value(
            REDDIT_CLIENT_SECRET
        )

        reddit_user_agent = self.has_value(
            REDDIT_USER_AGENT
        )

        if reddit_client_id and not reddit_client_secret:

            self.add_warning(
                "REDDIT_CLIENT_ID exists but "
                "REDDIT_CLIENT_SECRET is missing."
            )

        if reddit_client_secret and not reddit_client_id:

            self.add_warning(
                "REDDIT_CLIENT_SECRET exists but "
                "REDDIT_CLIENT_ID is missing."
            )

        if (
            reddit_client_id
            and
            reddit_client_secret
            and
            not reddit_user_agent
        ):

            self.add_warning(
                "Reddit credentials exist but "
                "REDDIT_USER_AGENT is missing."
            )

    # =====================================================
    # PRODUCTION RULES
    # =====================================================

    def validate_production(self):

        if APP_ENV != "production":

            return

        if API_HOST in {
            "127.0.0.1",
            "localhost",
        }:

            self.add_warning(
                "Production API_HOST is configured "
                "for localhost."
            )

        development_origins = {
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        }

        for origin in CORS_ORIGINS:

            if origin in development_origins:

                self.add_warning(
                    "Development CORS origin is being "
                    "used in production: "
                    f"{origin}"
                )

    # =====================================================
    # RUN ALL VALIDATION
    # =====================================================

    def validate(self):

        self.errors = []
        self.warnings = []

        self.validate_environment()
        self.validate_api()
        self.validate_database()
        self.validate_cors()
        self.validate_ai()
        self.validate_optional_services()
        self.validate_production()
        self.validate_production_settings()

        return {
            "valid": len(self.errors) == 0,
            "environment": APP_ENV,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def validate_production_settings(self):

        if not IS_PRODUCTION:
            return

        # =====================================================
        # API RELOAD
        # =====================================================

        if API_RELOAD:

            self.add_error(
                "API_RELOAD must be disabled in production."
            )


        # =====================================================
        # API HOST
        # =====================================================

        if API_HOST in (
            "127.0.0.1",
            "localhost"
        ):

            self.add_warning(
                "API_HOST is configured for localhost in production. "
                "Use 0.0.0.0 when exposing the application through "
                "a production container/server."
            )


        # =====================================================
        # CORS
        # =====================================================

        development_origins = {
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        }

        for origin in CORS_ORIGINS:

            if origin in development_origins:

                self.add_warning(
                    f"Development CORS origin '{origin}' "
                    "is enabled in production."
                )


        # =====================================================
        # SQLITE
        # =====================================================

        if DATABASE_URL.lower().startswith(
            "sqlite"
        ):

            self.add_warning(
                "SQLite is configured in production. "
                "Consider PostgreSQL for production deployment."
            )


        # =====================================================
        # AI MODEL
        # =====================================================

        if not OLLAMA_MODEL or not OLLAMA_MODEL.strip():

            self.add_error(
                "OLLAMA_MODEL must be configured in production."
            )


def validate_configuration():

    validator = ConfigurationValidator()

    return validator.validate()