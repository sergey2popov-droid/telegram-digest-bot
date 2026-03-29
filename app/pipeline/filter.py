import re
from app.core.dtos import ItemDTO

# Article age is enforced in the DB query (loader), not here.


TOPIC_WORDS = [
    # Здоровье / медицина (общее)
    "здоров",
    "болезн",
    "лечен",
    "лекарств",
    "аллерг",
    "витамин",
    "иммун",        # иммунитет, иммунная система
    "профилакт",
    "онколог",
    "симптом",
    "врач",
    "имплант",
    "медицин",      # медицина, медицинский
    "операц",       # операция
    "вакцин",       # вакцина, вакцинация
    "прививк",      # прививка
    "обследован",   # обследование
    "анализ",       # анализы крови и т.п.
    "диагноз",
    "реабилитац",   # реабилитация
    # Конкретные болезни и состояния
    "диабет",
    "гипертон",     # гипертония
    "инфаркт",
    "инсульт",
    "артрит",
    "астм",         # астма
    "ковид",
    "грипп",
    "рак",          # рак, раковый
    "аритми",       # аритмия
    "тромб",        # тромб, тромбоз
    "анеми",        # анемия
    "ожирен",       # ожирение
    "депресси",     # депрессия
    "деменци",      # деменция
    "аутоиммун",    # аутоиммунный
    # Органы и системы
    "сердц",        # сердце, сердечный
    "печен",        # печень
    "кишечн",       # кишечник
    "желудк",       # желудок
    "сустав",       # суставы
    "позвоночн",    # позвоночник
    "давлен",       # давление (кровяное)
    "холестер",     # холестерин
    "гормон",       # гормоны, гормональный
    "сосуд",        # сосуды, сосудистый
    "кров",         # кровь, кровяной
    "щитовидн",     # щитовидная железа
    # Питание
    "питан",
    "диет",
    "нутрици",
    "углевод",
    "белк",         # белки, белков (белок не покрывал падежи)
    "рецепт",
    "калор",
    "метабол",
    "клетчатк",     # клетчатка
    "сахар",        # сахар (кровяной)
    "кальци",       # кальций
    "магни",        # магний
    "омег",         # омега-3
    "жир",          # жиры, жирный
    "антиоксид",    # антиоксиданты
    # ЗОЖ / тело
    "зож",
    "фитнес",
    "активност",
    "похуд",
    "осанк",
    "сутулост",
    "закалив",      # закаливание
    "долголети",    # долголетие
    # Спорт (только фитнес / любительский)
    "ходьб",
    "бег",
    "плаван",
    "йог",          # йога
    "упражнен",     # упражнение
    "растяжк",      # растяжка
    # Психология и сон
    "психолог",
    "стресс",
    "тревог",
    "сон",
    "бессонниц",    # бессонница
    "выгоран",      # выгорание
    # Симптомы
    "кашел",        # кашель
    "насморк",
    "температур",   # температура тела
    "усталост",
    "боль",         # боль, болит
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
    import logging
    log = logging.getLogger(__name__)

    result: list[ItemDTO] = []

    c_title = c_url = c_russian = c_person = c_political = c_topic = 0

    for item in items:
        if not item.title:
            c_title += 1; continue
        if not item.url:
            c_url += 1; continue
        if not _is_russian(item.title):
            c_russian += 1; continue
        if _is_named_person_news(item.title):
            c_person += 1; continue
        if _is_political_legal(item.title):
            c_political += 1; continue
        if not _is_topic_match(item.title):
            c_topic += 1; continue
        result.append(item)

    log.info(
        "Filter: in=%d out=%d | dropped: no_title=%d no_url=%d not_ru=%d person=%d political=%d topic=%d",
        len(items), len(result), c_title, c_url, c_russian, c_person, c_political, c_topic,
    )
    return result
