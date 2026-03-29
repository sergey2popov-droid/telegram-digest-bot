import re
from datetime import datetime, timedelta, timezone

from app.core.dtos import ItemDTO

MAX_ARTICLE_AGE_DAYS = 1


TOPIC_WORDS = [
    # Здоровье / медицина
    "здоров",
    "болезн",
    "лечен",
    "лекарств",
    "аллерг",
    "витамин",
    "иммунит",
    "профилакт",
    "онколог",
    "симптом",
    "врач",
    "имплант",
    # Питание
    "питан",
    "диет",
    "нутрици",
    "углевод",
    "белок",
    "рецепт",
    "калор",
    "метабол",
    # ЗОЖ / тело
    "зож",
    "фитнес",
    "активност",
    "похуд",
    "осанк",
    "сутулост",
    # Спорт (только фитнес / любительский)
    "ходьб",
    "бег",
    "плаван",
    # Психология
    "психолог",
    "стресс",
    "тревог",
    # Сон
    "сон",
]
    

def _is_russian(title: str) -> bool:
    return any("\u0400" <= ch <= "\u04ff" for ch in title)


_NAMED_PERSON_RE = re.compile(
    r"^([А-ЯЁ][а-яёА-ЯЁ\-]+[\s\u00a0]){0,2}[А-ЯЁ][а-яёА-ЯЁ\-]+"
    r"(\s*[:\—]"
    r"|[\s\u00a0]+(рассказал|заявил|сообщил|признался|объяснил|высказался|"
    r"ответил|прокомментировал|назвал|поделился|отметил|добавил|"
    r"уточнил|подчеркнул|призвал|пообещал|опроверг|раскрыл|выразил|"
    r"выглядел|оказался|стал|был|показался|появился|прилетел|вернулся|"
    r"встретился|победил|проиграл|выступил|сыграл|забил|подписал|поставил)(а|и)?"
    r")"
)

_HEALTH_EXPERT_ROLES = {
    "врач", "врачи", "диетолог", "нутрициолог", "кардиолог", "психолог",
    "психиатр", "педиатр", "терапевт", "хирург", "невролог", "онколог",
    "эндокринолог", "гастроэнтеролог", "иммунолог", "физиотерапевт",
    "тренер", "нутрициологи", "диетологи", "специалист", "эксперт",
    "ученые", "учёные", "исследователи",
}


_POLITICAL_LEGAL_WORDS = [
    "возбуди",   # возбудили дело
    "халатн",    # халатность
    "уголовн",   # уголовное дело
    "задержа",   # задержали/задержан
    "арестов",   # арестовали
    "обвиняет",
    "приговор",
    "санкци",    # санкции
    "депутат",
    "министр",
    "президент",
    "губернатор",
    "политик",
    "парламент",
    "выборы",
    "голосован",
]


def _is_political_legal(title: str) -> bool:
    text = title.lower()
    tokens = re.split(r"[^\w]", text)
    return any(
        token.startswith(word)
        for token in tokens
        for word in _POLITICAL_LEGAL_WORDS
    )


_QUOTE_PREFIX_RE = re.compile(r'^«[^»]*»\s*[:\—]\s*')
_TWO_NAMES_RE = re.compile(r'^[А-ЯЁ][а-яёА-ЯЁ\-]+\s+[А-ЯЁ][а-яёА-ЯЁ\-]+[\s,]')
# Two consecutive capitalized Russian words (4+ chars each) anywhere in title
_INNER_TWO_NAMES_RE = re.compile(r'[А-ЯЁ][а-яё]{3,}\s+[А-ЯЁ][а-яё]{3,}')


def _is_named_person_news(title: str) -> bool:
    # Strip leading «quote»: block before checking
    stripped = _QUOTE_PREFIX_RE.sub('', title).strip()
    if not stripped:
        return False
    words = stripped.split()
    first_word = words[0].lower().rstrip(".,:")
    if first_word in _HEALTH_EXPERT_ROLES:
        # "Врач Фамилия глагол" — разрешаем (эксперт с фамилией даёт совет)
        # "Психолог Имя Фамилия глагол" — запрещаем (полное имя = celebrity gossip)
        if len(words) >= 3 and words[1][0].isupper() and words[2][0].isupper():
            return True
        return False
    # Two consecutive capitalized words at start = Name Surname
    if _TWO_NAMES_RE.match(stripped):
        return True
    # Name + speech verb at start
    if _NAMED_PERSON_RE.match(stripped):
        return True
    # Two consecutive capitalized words anywhere inside title = "Как Алла Пугачева похудела"
    if _INNER_TWO_NAMES_RE.search(stripped):
        return True
    return False


def _is_topic_match(title: str) -> bool:
    if not title:
        return False

    tokens = re.split(r"[^\w]", title.lower())
    return any(
        token.startswith(word)
        for token in tokens
        for word in TOPIC_WORDS
    )


def filter_valid(items: list[ItemDTO]) -> list[ItemDTO]:
    result: list[ItemDTO] = []
    max_age_cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_ARTICLE_AGE_DAYS)

    for item in items:
        if not item.title:
            continue
        if not item.url:
            continue
        if item.published_at and item.published_at < max_age_cutoff:
            continue
        if not _is_russian(item.title):
            continue
        if _is_named_person_news(item.title):
            continue
        if _is_political_legal(item.title):
            continue
        if not _is_topic_match(item.title):
            continue

        result.append(item)

    return result
