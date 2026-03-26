"""
Scoring logic.

For Telegram sources (reactions > 0 or comments > 0):
    score = reactions + comments  — real user engagement.

For RSS sources (reactions = 0, comments = 0):
    score = title-based estimate of reader interest.

Freshness is not factored in — the pipeline already restricts
items to the last 24 hours, so all candidates are equally fresh.
"""

_TRIGGER_WORDS = [
    # Russian engagement triggers
    "оказалось", "выяснили", "раскрыли", "рассекретили", "секрет",
    "учёные", "врачи", "исследование", "доказано", "запрещено",
    "опасно", "вредно", "польза", "поможет", "спасёт",
    # Fitness / health specifics
    "похудеть", "похудел", "сжигает", "ускоряет", "замедляет",
    "норма", "дефицит", "переизбыток", "симптом",
]

_HOW_WHY_WORDS = ["как ", "почему ", "зачем ", "когда ", "сколько "]


def _title_score(title: str) -> float:
    """Estimate reader interest from the title alone (RSS fallback)."""
    if not title:
        return 0.0

    score = 0.0
    t = title.lower()

    # Numbers suggest list-articles or stats ("7 продуктов...", "минус 5 кг")
    if any(ch.isdigit() for ch in title):
        score += 0.5

    # Question mark — reader wants the answer
    if "?" in title:
        score += 0.3

    # How/why words — informational hooks
    for word in _HOW_WHY_WORDS:
        if word in t:
            score += 0.3
            break  # count once

    # Engagement trigger words
    for word in _TRIGGER_WORDS:
        if word in t:
            score += 0.5

    return score


def compute_score(reactions: int, comments: int, title: str = "") -> float:
    """
    Primary signal: real user engagement (Telegram sources).
    Fallback signal: title quality (RSS sources where engagement = 0).
    """
    if reactions > 0 or comments > 0:
        return float(reactions + comments)
    return _title_score(title)


def compute_ranking_score(score: float) -> float:
    """
    No freshness adjustment — 24-hour window already ensures recency.
    Returns score unchanged.
    """
    return score
