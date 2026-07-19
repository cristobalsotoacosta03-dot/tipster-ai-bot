"""
Curated list of commonly-requested team names, used only to correct typos
before spending an API-Football request - not a source of truth for team
data (that's always the live API). Covers La Liga, top European clubs, and
national teams likely to come up for a Spanish-speaking betting audience.
"""
import difflib
from typing import Optional

KNOWN_TEAMS = [
    # La Liga
    "Real Madrid", "Barcelona", "Atletico Madrid", "Real Sociedad",
    "Real Betis", "Sevilla", "Villarreal", "Athletic Club", "Valencia",
    "Girona", "Osasuna", "Celta Vigo", "Rayo Vallecano", "Getafe",
    "Mallorca", "Las Palmas", "Alaves", "Espanyol", "Leganes", "Valladolid",
    # Top European clubs
    "Manchester City", "Manchester United", "Liverpool", "Chelsea",
    "Arsenal", "Tottenham", "Bayern Munich", "Borussia Dortmund",
    "Paris Saint Germain", "Juventus", "AC Milan", "Inter Milan",
    "Napoli", "AS Roma", "Benfica", "Porto", "Ajax",
    # National teams
    "España", "Argentina", "Brasil", "Francia", "Alemania", "Italia",
    "Inglaterra", "Portugal", "Uruguay", "Colombia", "Mexico", "Chile",
]


def correct_team_name_typo(team_name: str, cutoff: float = 0.8) -> Optional[str]:
    """
    If `team_name` looks like a near-miss typo of a well-known team (e.g.
    "Real Madrd" -> "Real Madrid"), return the corrected name. Returns None
    when there's no close-enough match, including when `team_name` already
    matches exactly (nothing to correct) or is too different to guess
    safely - callers should fall back to the original name in that case.
    """
    normalized = team_name.strip()
    if not normalized:
        return None

    matches = difflib.get_close_matches(
        normalized, KNOWN_TEAMS, n=1, cutoff=cutoff
    )
    if not matches or matches[0] == normalized:
        return None
    return matches[0]
