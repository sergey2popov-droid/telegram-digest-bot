AGE_FLOOR_HOURS = 1.0


def compute_score(reactions: int, comments: int) -> float:
    """raw_score = reactions + comments."""
    return float(reactions + comments)


def compute_ranking_score(score: float, age_hours: float) -> float:
    """ranking_score = score / age_hours, age floored at 1 hour."""
    return score / max(age_hours, AGE_FLOOR_HOURS)
