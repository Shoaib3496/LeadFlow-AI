import json
import os


# ============================================================
# NOTIFICATION SETTINGS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

SETTINGS_FILE = os.path.join(
    PROJECT_ROOT,
    "config",
    "notification_settings.json"
)

DEFAULT_NOTIFICATION_SETTINGS = {
    "hotLead": True,
    "pipelineCompleted": True,
    "pipelineFailed": True,
}


def get_notification_settings():
    """
    Load notification preferences from persistent storage.
    If the file does not exist or is invalid, return defaults.
    """

    try:

        if not os.path.exists(SETTINGS_FILE):
            return DEFAULT_NOTIFICATION_SETTINGS.copy()

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        settings = DEFAULT_NOTIFICATION_SETTINGS.copy()

        if isinstance(data, dict):

            for key in settings:

                if key in data:
                    settings[key] = bool(data[key])

        return settings

    except Exception as e:

        print(
            f"Notification settings load failed: {e}"
        )

        return DEFAULT_NOTIFICATION_SETTINGS.copy()


def save_notification_settings(settings):
    """
    Persist notification preferences.
    """

    os.makedirs(
        os.path.dirname(SETTINGS_FILE),
        exist_ok=True
    )

    updated = DEFAULT_NOTIFICATION_SETTINGS.copy()

    if isinstance(settings, dict):

        for key in updated:

            if key in settings:
                updated[key] = bool(settings[key])

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            updated,
            file,
            indent=4
        )

    return updated


# ============================================================
# NOTIFICATION WRITER
# ============================================================

def _write_notification(message):

    log_file = os.path.join(
        PROJECT_ROOT,
        "notifications.log"
    )

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            message + "\n"
        )

    print(
        f"Notification Sent: {message}"
    )


# ============================================================
# NEW LEAD
# ============================================================

def notify_new_lead(title, score):

    _write_notification(
        f"NEW LEAD | Score: {score} | {title}"
    )


# ============================================================
# HOT LEAD
# ============================================================

def notify_hot_lead(
    title,
    platform,
    score,
    priority,
    budget
):

    settings = get_notification_settings()

    if not settings["hotLead"]:
        print(
            "HOT lead notification skipped "
            "(disabled in Settings)."
        )
        return

    message = (
        "🔥 HOT LEAD DETECTED\n"
        f"Title: {title}\n"
        f"Platform: {platform}\n"
        f"Score: {score}\n"
        f"Priority: {priority}\n"
        f"Budget: {budget}"
    )

    _write_notification(message)


# ============================================================
# PIPELINE COMPLETED
# ============================================================

def notify_pipeline_completed(
    collected,
    buyer_intent_rejected,
    business_fit_rejected,
    duplicates,
    saved
):

    settings = get_notification_settings()

    if not settings["pipelineCompleted"]:
        print(
            "Pipeline completion notification skipped "
            "(disabled in Settings)."
        )
        return

    message = (
        "✅ PIPELINE COMPLETED\n"
        f"Collected: {collected}\n"
        f"Buyer Intent Rejected: {buyer_intent_rejected}\n"
        f"Business Fit Rejected: {business_fit_rejected}\n"
        f"Duplicates: {duplicates}\n"
        f"Saved: {saved}"
    )

    _write_notification(message)


# ============================================================
# PIPELINE FAILED
# ============================================================

def notify_pipeline_failed(error):

    settings = get_notification_settings()

    if not settings["pipelineFailed"]:
        print(
            "Pipeline failure notification skipped "
            "(disabled in Settings)."
        )
        return

    message = (
        "❌ PIPELINE FAILED\n"
        f"Error: {error}"
    )

    _write_notification(message)
