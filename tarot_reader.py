"""
tarot_reader.py — Pure ML weight engine + card logic.
CLI display has been moved to cli.py.
"""

import json
import random
import os
import math
from datetime import datetime, date
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────

SOFTMAX_TEMP = 0.3   # Lower = more deterministic; higher = more random

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "cards.json")
try:
    with open(DATA_PATH, encoding="utf-8") as f:
        CARDS = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(
        f"Card data not found at {DATA_PATH}. "
        "Make sure data/cards.json exists relative to tarot_reader.py."
    )

# ─────────────────────────────────────────────
#  NUMEROLOGY
# ─────────────────────────────────────────────

def life_path_number(birthdate_str: str) -> int:
    """Reduce a birthdate (YYYY-MM-DD) to a life path digit (1–9, or master 11/22)."""
    digits = [int(d) for d in birthdate_str if d.isdigit()]
    total  = sum(digits)

    # Reduce until we reach a master number or single digit
    while total > 9 and total not in (11, 22):
        total = sum(int(d) for d in str(total))

    return total


def numerology_score(card: dict, life_path: int) -> float:
    """Return a weight boost if the card has affinity with this life path number."""
    if life_path in card.get("numerology_affinity", []):
        return 1.3
    return 1.0


# ─────────────────────────────────────────────
#  ASTROLOGY (sun sign from birthdate)
# ─────────────────────────────────────────────

# Each entry: (sign, (start_month, start_day), (end_month, end_day))
SIGN_DATE_RANGES = [
    ("capricorn",   (12, 22), (12, 31)),   # Dec 22–31 (Jan portion handled separately)
    ("capricorn",   (1,   1), (1,  19)),   # Jan 1–19
    ("aquarius",    (1,  20), (2,  18)),
    ("pisces",      (2,  19), (3,  20)),
    ("aries",       (3,  21), (4,  19)),
    ("taurus",      (4,  20), (5,  20)),
    ("gemini",      (5,  21), (6,  20)),
    ("cancer",      (6,  21), (7,  22)),
    ("leo",         (7,  23), (8,  22)),
    ("virgo",       (8,  23), (9,  22)),
    ("libra",       (9,  23), (10, 22)),
    ("scorpio",     (10, 23), (11, 21)),
    ("sagittarius", (11, 22), (12, 21)),
]

SIGN_CARD_AFFINITIES = {
    "aries":       ["The Emperor", "The Tower", "Strength", "Two of Wands", "King of Wands"],
    "taurus":      ["The Empress", "The Hierophant", "Four of Pentacles", "Nine of Pentacles"],
    "gemini":      ["The Lovers", "The Magician", "Eight of Wands", "Page of Swords"],
    "cancer":      ["The Chariot", "The High Priestess", "Three of Cups", "Ten of Cups"],
    "leo":         ["Strength", "The Sun", "Six of Wands", "King of Wands", "Queen of Wands"],
    "virgo":       ["The Hermit", "Eight of Pentacles", "Knight of Pentacles", "Page of Pentacles"],
    "libra":       ["Justice", "The Empress", "Two of Cups", "Six of Pentacles"],
    "scorpio":     ["Death", "The Moon", "The Devil", "Ten of Swords", "Judgement"],
    "sagittarius": ["Wheel of Fortune", "Temperance", "Eight of Wands", "Three of Wands"],
    "capricorn":   ["The Devil", "The World", "Four of Pentacles", "King of Pentacles"],
    "aquarius":    ["The Star", "The Fool", "Page of Swords", "Ace of Swords"],
    "pisces":      ["The Moon", "The Hanged Man", "The Star", "Queen of Cups", "Ten of Cups"],
}


def get_sun_sign(birthdate_str: str) -> str:
    """Derive the sun sign from a YYYY-MM-DD birthdate string."""
    dt    = datetime.strptime(birthdate_str, "%Y-%m-%d")
    month = dt.month
    day   = dt.day

    for sign, (sm, sd), (em, ed) in SIGN_DATE_RANGES:
        # Same-month range (e.g. Mar 21 – Apr 19 doesn't cross a month boundary here
        # because each entry shares the same start/end month or we split them above)
        if sm == em:
            if month == sm and sd <= day <= ed:
                return sign
        else:
            # Cross-month range: start month OR end month
            if (month == sm and day >= sd) or (month == em and day <= ed):
                return sign

    return "capricorn"  # should never be reached with the explicit ranges above


def astrology_score(card: dict, sun_sign: str) -> float:
    """Boost cards affiliated with the user's sun sign."""
    if card["name"] in SIGN_CARD_AFFINITIES.get(sun_sign, []):
        return 1.2
    return 1.0


# ─────────────────────────────────────────────
#  SEMANTIC SCORING (keyword overlap + TF-IDF hybrid)
# ─────────────────────────────────────────────

QUERY_EXPANSIONS = {
    "love":       ["love", "romance", "relationship", "partner", "attraction", "heart", "connection", "union", "passion", "feelings"],
    "career":     ["career", "work", "job", "success", "achievement", "ambition", "profession", "money", "business", "skill"],
    "money":      ["money", "wealth", "finance", "abundance", "prosperity", "security", "material", "savings", "income"],
    "health":     ["health", "healing", "body", "energy", "vitality", "strength", "wellbeing", "recovery", "rest"],
    "family":     ["family", "home", "community", "togetherness", "support", "nurturing", "belonging", "children"],
    "future":     ["future", "destiny", "fate", "path", "direction", "change", "transformation", "what", "next"],
    "luck":       ["luck", "fortune", "chance", "destiny", "opportunity", "change", "cycle", "fate", "karma"],
    "friendship": ["friendship", "community", "support", "trust", "bond", "connection", "social", "friend"],
    "travel":     ["travel", "journey", "adventure", "movement", "change", "discovery", "freedom", "abroad"],
    "spiritual":  ["spiritual", "soul", "intuition", "inner", "wisdom", "consciousness", "awakening", "purpose"],
    "anxiety":    ["anxiety", "fear", "worry", "stress", "overwhelm", "uncertainty", "confusion", "unknown"],
    "change":     ["change", "transition", "transformation", "new", "shift", "ending", "beginning", "release"],
}

# Build reverse lookup so any expansion word also triggers its group
# e.g. "fortune" triggers the "luck" group, "romance" triggers the "love" group
_REVERSE_EXPANSIONS = {}
for _key, _words in QUERY_EXPANSIONS.items():
    for _w in _words:
        if _w not in _REVERSE_EXPANSIONS:
            _REVERSE_EXPANSIONS[_w] = set()
        _REVERSE_EXPANSIONS[_w].update(_words)

# Pre-build the card theme corpus once (never changes at runtime)
_CARD_DOCS = [c["themes"] for c in CARDS]


def _get_query_tokens(question: str) -> set:
    """Expand the question into a full set of semantic tokens (bidirectional matching)."""
    q_lower = question.lower()
    tokens  = set(q_lower.split())
    expanded = set()
    for t in tokens:
        # Check both the primary key and the reverse lookup
        if t in QUERY_EXPANSIONS:
            expanded.update(QUERY_EXPANSIONS[t])
        if t in _REVERSE_EXPANSIONS:
            expanded.update(_REVERSE_EXPANSIONS[t])
    tokens.update(expanded)
    return tokens


@lru_cache(maxsize=128)
def build_semantic_scores(question: str) -> np.ndarray:
    """
    Score each card by direct token overlap with the expanded query,
    blended with TF-IDF cosine similarity (60/40), then log-scaled.

    Result is cached by question string so repeated draws don't refit
    the vectoriser.
    """
    query_tokens = _get_query_tokens(question)

    # Keyword overlap signal (whole-word matching)
    keyword_scores = np.zeros(len(CARDS))
    for i, card in enumerate(CARDS):
        card_tokens = set(card["themes"].lower().split())
        overlap     = len(query_tokens & card_tokens)
        # Match query tokens against individual words within each keyword phrase
        kw_overlap  = sum(
            1 for kw in card["keywords"]
            if any(t == kw.lower() or t in kw.lower().split() for t in query_tokens)
        )
        keyword_scores[i] = overlap + kw_overlap

    # TF-IDF signal
    expanded     = question + " " + " ".join(query_tokens)
    all_docs     = [expanded] + _CARD_DOCS
    vectorizer   = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    tfidf_sims   = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:]).flatten()

    # Normalize both signals to [0, 1] before blending
    kw_max = keyword_scores.max()
    if kw_max > 0:
        keyword_scores = keyword_scores / kw_max

    tf_max = tfidf_sims.max()
    if tf_max > 0:
        tfidf_sims = tfidf_sims / tf_max

    # Blend 60% keyword, 40% TF-IDF (both now in [0, 1])
    blended = (keyword_scores * 0.6) + (tfidf_sims * 0.4)

    return blended


# ─────────────────────────────────────────────
#  SOFTMAX
# ─────────────────────────────────────────────

def softmax(x: np.ndarray, temperature: float = SOFTMAX_TEMP) -> np.ndarray:
    """
    Converts raw scores into a probability distribution.
    Lower temperature = more deterministic; higher = more random.
    """
    x   = np.array(x, dtype=float) / temperature
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


# ─────────────────────────────────────────────
#  WEIGHT ENGINE
# ─────────────────────────────────────────────

def compute_weights(question: str, life_path: int, sun_sign: str) -> np.ndarray:
    """
    Combine keyword+TF-IDF semantic scores, numerology, and astrology
    into a final probability distribution over all 78 cards.
    """
    semantic_scores = build_semantic_scores(question)

    # Normalize semantic to [0.5, 1.5] so no card is zeroed out
    # and numerology/astrology boosts stay proportional
    s_min, s_max = semantic_scores.min(), semantic_scores.max()
    if s_max > s_min:
        normalized = (semantic_scores - s_min) / (s_max - s_min)
    else:
        normalized = np.ones_like(semantic_scores)
    normalized = normalized + 0.5

    combined = np.array([
        normalized[i]
        * numerology_score(CARDS[i], life_path)
        * astrology_score(CARDS[i], sun_sign)
        for i in range(len(CARDS))
    ])

    return softmax(combined)


def compute_weights_debug(question: str, life_path: int, sun_sign: str) -> dict:
    """Return full breakdown of weight computation for diagnostics."""
    semantic_scores = build_semantic_scores(question)

    s_min, s_max = semantic_scores.min(), semantic_scores.max()
    if s_max > s_min:
        normalized = (semantic_scores - s_min) / (s_max - s_min)
    else:
        normalized = np.ones_like(semantic_scores)
    normalized = normalized + 0.5

    breakdown = []
    for i, card in enumerate(CARDS):
        sem = float(normalized[i])
        num = numerology_score(card, life_path)
        ast = astrology_score(card, sun_sign)
        combined = sem * num * ast
        breakdown.append({
            "index": i,
            "name": card["name"],
            "semantic_raw": round(float(semantic_scores[i]), 4),
            "semantic_norm": round(sem, 4),
            "numerology": num,
            "astrology": ast,
            "combined_raw": round(combined, 4),
        })

    raw = np.array([b["combined_raw"] for b in breakdown])
    probs = softmax(raw)

    for i, b in enumerate(breakdown):
        b["probability"] = round(float(probs[i]) * 100, 4)

    breakdown.sort(key=lambda x: x["probability"], reverse=True)

    return {
        "breakdown": breakdown,
        "top_10": breakdown[:10],
        "bottom_10": breakdown[-10:],
        "prob_range": (breakdown[-1]["probability"], breakdown[0]["probability"]),
        "entropy": float(-np.sum(probs * np.log(probs + 1e-10))),
        "max_entropy": float(np.log(len(CARDS))),
    }


# ─────────────────────────────────────────────
#  CARD DRAWING
# ─────────────────────────────────────────────

def draw_cards(question: str, life_path: int, sun_sign: str, n: int = 3) -> list:
    weights = compute_weights(question, life_path, sun_sign)

    card_indices = np.random.choice(
        len(CARDS),
        size=n,
        replace=False,
        p=weights
    )

    drawn = []
    for idx in card_indices:
        card             = CARDS[idx].copy()
        card["position"] = random.choice(["upright", "reversed"])
        card["weight"]   = round(float(weights[idx]) * 100, 3)

        # Pre-compute which signals fired for this card (used in UI)
        card["ast_match"] = card["name"] in SIGN_CARD_AFFINITIES.get(sun_sign, [])
        card["num_match"] = life_path in card.get("numerology_affinity", [])

        drawn.append(card)
    return drawn


# ─────────────────────────────────────────────
#  READING ENGINE  (plain-text, no rich markup)
# ─────────────────────────────────────────────

POSITION_LABELS = ["Past / Foundation", "Present / Challenge", "Future / Outcome"]

PAST_TEMPLATES = [
    "The {name} has shaped the ground beneath your question — {meaning_fragment}, and the echoes of {kw0} and {kw1} still linger.",
    "Looking back, {name} speaks of {meaning_fragment}. This foundation of {kw0} is what brought you here.",
    "{name} reveals the roots of your path: {meaning_fragment}. The shadow of {kw0} runs deep.",
]
PRESENT_TEMPLATES = [
    "Right now, {name} sits at the heart of things — {meaning_fragment}. You are being asked to reckon with {kw0} and {kw1}.",
    "In this moment, {name} holds up a mirror: {meaning_fragment}. The energy of {kw0} is alive and pressing.",
    "{name} defines your present challenge — {meaning_fragment}. Notice how {kw0} is pulling at you.",
]
FUTURE_TEMPLATES = [
    "The path ahead is lit by {name}: {meaning_fragment}. Let {kw0} and {kw1} be your compass.",
    "Moving forward, {name} promises {meaning_fragment}. Trust the current of {kw0} to carry you.",
    "{name} awaits you — {meaning_fragment}. The energy of {kw0} is yours to step into.",
]

# Reversed variants — tone-matched for shadow/challenge energy
# These use kw0/kw1 as thematic anchors, not restating the meaning
PAST_TEMPLATES_REV = [
    "In its reversed form, {name} casts a shadow over your foundation — {meaning_fragment}. The theme of {kw0} has been quietly shaping things beneath the surface.",
    "Looking back, {name} reversed points to {meaning_fragment}. Something around {kw1} was left unresolved and still colours the present.",
    "{name} reversed reveals a hidden root: {meaning_fragment}. This is old energy, and it runs deeper than it appears.",
]
PRESENT_TEMPLATES_REV = [
    "Right now, {name} reversed asks you to look inward — {meaning_fragment}. There is tension here that wants your honest attention.",
    "In this moment, {name} reversed holds up an uncomfortable mirror: {meaning_fragment}. Sit with what comes up before pushing forward.",
    "{name} reversed marks a turning point — {meaning_fragment}. The real work lives in what you have been avoiding.",
]
FUTURE_TEMPLATES_REV = [
    "Ahead, {name} reversed is a gentle warning — {meaning_fragment}. Be mindful of {kw1} as you move forward.",
    "{name} reversed suggests the road ahead asks for honesty: {meaning_fragment}. Working through this will clear the way.",
    "The future holds {name} reversed — {meaning_fragment}. This is not a dead end, but it needs your conscious attention.",
]

ALL_TEMPLATES     = [PAST_TEMPLATES, PRESENT_TEMPLATES, FUTURE_TEMPLATES]
ALL_TEMPLATES_REV = [PAST_TEMPLATES_REV, PRESENT_TEMPLATES_REV, FUTURE_TEMPLATES_REV]


def _sentence_fragment(meaning: str) -> str:
    """Strip trailing period and lowercase for mid-sentence embedding."""
    return meaning.rstrip(".").lower()


def _reversed_keywords(card: dict) -> list[str]:
    """Extract keyword-like phrases from the reversed_meaning string."""
    meaning = card.get("reversed_meaning", "")
    # Split on commas, strip, take first few as pseudo-keywords
    parts = [p.strip().lower().rstrip(".") for p in meaning.split(",") if p.strip()]
    # Deduplicate against each other (first 4 unique, pick up to 3)
    seen = []
    for p in parts:
        if not any(p in s or s in p for s in seen):
            seen.append(p)
        if len(seen) >= 3:
            break
    return seen if seen else card["keywords"][:3]


def generate_reading_plain(question: str, drawn_cards: list) -> list[dict]:
    """
    Return a list of dicts, one per card, with plain-text reading sentences.
    No rich/HTML markup — safe for any renderer.
    """
    results = []
    for i, card in enumerate(drawn_cards):
        label    = POSITION_LABELS[i] if i < len(POSITION_LABELS) else f"Card {i+1}"
        is_rev   = card["position"] == "reversed"
        meaning  = card["upright_meaning"] if not is_rev else card["reversed_meaning"]
        keywords = _reversed_keywords(card) if is_rev else card["keywords"]
        tpl_set  = ALL_TEMPLATES_REV[i] if is_rev and i < len(ALL_TEMPLATES_REV) else (ALL_TEMPLATES[i] if i < len(ALL_TEMPLATES) else FUTURE_TEMPLATES)
        template = tpl_set[card.get("number", 0) % len(tpl_set)]

        sentence = template.format(
            name             = card["name"],
            meaning_fragment = _sentence_fragment(meaning),
            keywords         = ", ".join(keywords[:3]),
            kw0              = keywords[0] if keywords else "",
            kw1              = keywords[1] if len(keywords) > 1 else keywords[0],
            element          = card.get("element", "mystery").capitalize(),
        )

        results.append({
            "label":    label,
            "name":     card["name"],
            "position": card["position"],
            "sentence": sentence,
            "meaning":  meaning,
            "keywords": keywords,
        })
    return results