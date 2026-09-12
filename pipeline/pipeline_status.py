import threading
from datetime import datetime


# ==========================================
# THREAD SAFE PIPELINE STATUS
# ==========================================

_lock = threading.Lock()


_status = {

    "state": "IDLE",

    "started_at": None,

    "finished_at": None,

    "error": None,

    "result": None
}


# ==========================================
# GET CURRENT STATUS
# ==========================================

def get_pipeline_status():

    with _lock:

        return _status.copy()


# ==========================================
# PIPELINE STARTED
# ==========================================

def mark_running():

    with _lock:

        _status["state"] = "RUNNING"

        _status["started_at"] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        _status["finished_at"] = None

        _status["error"] = None

        _status["result"] = None


# ==========================================
# PIPELINE COMPLETED
# ==========================================

def mark_completed(result=None):

    with _lock:

        _status["state"] = "COMPLETED"

        _status["finished_at"] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        _status["error"] = None

        _status["result"] = result


# ==========================================
# PIPELINE FAILED
# ==========================================

def mark_failed(error):

    with _lock:

        _status["state"] = "FAILED"

        _status["finished_at"] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        _status["error"] = str(error)

        _status["result"] = None