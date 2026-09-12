import threading
from collections import deque
from datetime import datetime


class DashboardPerformanceMonitor:

    def __init__(self, window_size=20):

        self.lock = threading.Lock()

        # Keep only the most recent requests for current performance.
        self.response_times = deque(maxlen=window_size)

        self.last_response_time = 0.0
        self.fastest_response_time = None
        self.slowest_response_time = 0.0
        self.last_measured_at = None

    # ---------------------------------------------------------
    # Record dashboard request
    # ---------------------------------------------------------

    def record(self, duration_seconds):

        duration_ms = round(
            duration_seconds * 1000,
            2
        )

        with self.lock:

            self.response_times.append(duration_ms)

            self.last_response_time = duration_ms

            # Fastest request in current window
            if (
                self.fastest_response_time is None
                or duration_ms < self.fastest_response_time
            ):
                self.fastest_response_time = duration_ms

            # Slowest request in current window
            self.slowest_response_time = max(
                self.response_times
            )

            self.last_measured_at = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

    # ---------------------------------------------------------
    # Average response time
    # ---------------------------------------------------------

    def get_average(self):

        with self.lock:

            if not self.response_times:
                return 0.0

            return round(
                sum(self.response_times)
                /
                len(self.response_times),
                2
            )

    # ---------------------------------------------------------
    # Performance status
    # ---------------------------------------------------------

    def get_status(self):

        with self.lock:

            if not self.response_times:

                average = 0.0

            else:

                average = round(
                    sum(self.response_times)
                    /
                    len(self.response_times),
                    2
                )

            if average == 0:

                status = "NO DATA"

            elif average < 500:

                status = "EXCELLENT"

            elif average < 1000:

                status = "GOOD"

            elif average < 2000:

                status = "SLOW"

            else:

                status = "CRITICAL"

            return {

                "status": status,

                "dashboard_requests":
                    len(self.response_times),

                "last_response_time_ms":
                    self.last_response_time,

                "average_response_time_ms":
                    average,

                "fastest_response_time_ms":
                    self.fastest_response_time,

                "slowest_response_time_ms":
                    self.slowest_response_time,

                "last_measured_at":
                    self.last_measured_at
            }


dashboard_performance = DashboardPerformanceMonitor()