from datetime import datetime
from threading import Lock


class ScraperHealthTracker:

    def __init__(self):

        self._lock = Lock()

        self._health = {}

    def start(self, source_name):

        with self._lock:

            self._health[source_name] = {
                "source": source_name,
                "status": "RUNNING",
                "last_run": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "leads_collected": 0,
                "error": None
            }

    def success(self, source_name, leads_collected):

        with self._lock:

            status = (
                "HEALTHY"
                if leads_collected > 0
                else "DEGRADED"
            )

            self._health[source_name] = {
                "source": source_name,
                "status": status,
                "last_run": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "leads_collected": leads_collected,
                "error": None
            }

    def failure(self, source_name, error):

        with self._lock:

            self._health[source_name] = {
                "source": source_name,
                "status": "FAILED",
                "last_run": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "leads_collected": 0,
                "error": str(error)
            }

    def get_all(self):

        with self._lock:

            return list(
                self._health.values()
            )


scraper_health = ScraperHealthTracker()