"""
Keyword-heuristic extraction of a betting "pick" from a single tipster
message - not NLP, just enough structure to aggregate across channels.
Intentionally does not keep the original message text on the returned
signal: only the extracted team/direction/confidence survive, so nothing
downstream can accidentally re-publish a tipster's literal wording.
"""
from dataclasses import dataclass
from typing import List, Optional
import re
import unicodedata

DIRECTION_HOME = "home"
DIRECTION_AWAY = "away"
DIRECTION_OVER = "over"
DIRECTION_UNDER = "under"
DIRECTION_BTTS_YES = "btts_yes"
DIRECTION_BTTS_NO = "btts_no"

_OVER_PATTERNS = [r"\bmas de 2[.,]5\b", r"\bover\b", r"\bm[aá]s de 2\.5\b"]
_UNDER_PATTERNS = [r"\bmenos de 2[.,]5\b", r"\bunder\b"]
_BTTS_YES_PATTERNS = [r"\bambos marcan\b", r"\bbtts\s*s[ií]\b", r"^btts$"]
_BTTS_NO_PATTERNS = [r"\bno marcan ambos\b", r"\bbtts\s*no\b"]

_HOME_KEYWORDS = ["gana en casa", "favorito local", "local gana", "gana de local"]
_AWAY_KEYWORDS = ["gana fuera", "favorito visitante", "visitante gana", "gana de visitante"]

_CONFIDENCE_RE = re.compile(r"(\d{1,3})\s*%\s*(?:de\s*)?confianza", re.IGNORECASE)


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


def _matches_any(text: str, patterns: List[str]) -> bool:
    return any(re.search(p, text) for p in patterns)


def _team_mentioned(text: str, team_name: str) -> bool:
    """Matches on the full team name, or on any distinctive word from it
    (>= 5 letters, e.g. 'Madrid', 'Atletico'), so a tipster writing just
    'El Atlético gana...' still counts as mentioning 'Atletico Madrid'."""
    normalized_team = _normalize(team_name)
    if not normalized_team:
        return False
    if normalized_team in text:
        return True
    for word in normalized_team.split():
        if len(word) >= 5 and re.search(rf"\b{re.escape(word)}\b", text):
            return True
    return False


@dataclass
class TipperSignal:
    """A single channel's extracted pick for one match - never carries the
    original message text."""
    direction: Optional[str]  # one of the DIRECTION_* constants, or None
    confidence_pct: Optional[int] = None


def detect_signal(
    message_text: str,
    home_team: str,
    away_team: str,
) -> Optional[TipperSignal]:
    """
    Best-effort extraction of a pick for a specific match from one tipster
    message. Returns None when the message doesn't look like a pick for
    this match at all (wrong match, or no recognizable signal).
    """
    if not message_text:
        return None

    normalized = _normalize(message_text)

    mentions_home = _team_mentioned(normalized, home_team)
    mentions_away = _team_mentioned(normalized, away_team)
    if not mentions_home and not mentions_away:
        return None

    direction: Optional[str] = None

    if _matches_any(normalized, _OVER_PATTERNS):
        direction = DIRECTION_OVER
    elif _matches_any(normalized, _UNDER_PATTERNS):
        direction = DIRECTION_UNDER
    elif _matches_any(normalized, _BTTS_NO_PATTERNS):
        direction = DIRECTION_BTTS_NO
    elif _matches_any(normalized, _BTTS_YES_PATTERNS):
        direction = DIRECTION_BTTS_YES
    elif mentions_home and _matches_any(normalized, _HOME_KEYWORDS):
        direction = DIRECTION_HOME
    elif mentions_away and _matches_any(normalized, _AWAY_KEYWORDS):
        direction = DIRECTION_AWAY
    elif mentions_home and not mentions_away:
        # Only the home team is mentioned with no explicit "gana fuera" -
        # treat a bare mention as a soft lean towards that team.
        direction = DIRECTION_HOME
    elif mentions_away and not mentions_home:
        direction = DIRECTION_AWAY

    if direction is None:
        return None

    confidence_match = _CONFIDENCE_RE.search(normalized)
    confidence_pct = int(confidence_match.group(1)) if confidence_match else None

    return TipperSignal(direction=direction, confidence_pct=confidence_pct)
