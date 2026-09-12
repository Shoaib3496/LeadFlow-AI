import re

REJECT_PATTERNS = [
    r"\bshow hn\b",
    r"\btutorial\b",
    r"\bguide\b",
    r"\bintroducing\b",
    r"\brelease\b",
    r"\blaunch\b",
    r"\bweekly\b",
    r"\bnewsletter\b",
    r"\bbenchmark\b",
    r"\bopen source\b",
    r"\bgithub\b",
    r"\bdocumentation\b",
]

POSITIVE_PATTERNS = [
    r"\bneed\b",
    r"\blooking for\b",
    r"\bhire\b",
    r"\bhiring\b",
    r"\bdeveloper\b",
    r"\bwebsite\b",
    r"\bweb app\b",
    r"\bmobile app\b",
    r"\bsoftware\b",
    r"\bcrm\b",
    r"\bautomation\b",
    r"\bchatbot\b",
    r"\bapi\b",
    r"\bintegration\b",
    r"\bproject\b",
]


def should_process(lead):

    text = f"{lead['title']} {lead['description']}".lower()

    for pattern in REJECT_PATTERNS:
        if re.search(pattern, text):
            return False

    for pattern in POSITIVE_PATTERNS:
        if re.search(pattern, text):
            return True

    return True