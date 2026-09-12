import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notifications.notifier import notify_new_lead

notify_new_lead(
    "Need website for restaurant",
    80
)