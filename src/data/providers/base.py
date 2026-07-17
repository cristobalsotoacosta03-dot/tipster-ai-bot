"""
Data provider contract for football match data.

`StatsFetcher` (src/data/stats_fetcher.py, API-Football) is the primary
implementation. `FootballDataOrgProvider` and `TheSportsDbProvider` (both in
this package) implement the same contract as free, legitimate fallback
sources - used by `MatchAnalyzer` only when API-Football can't find one of
the two teams. League context follows the same plain-dict shape API-Football
already uses ({"league_id", "league_name", "season"}) rather than a
dataclass, so downstream code doesn't need to care which provider produced it.
"""
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class TeamRef:
    id: int
    name: str
    country: Optional[str] = None


@dataclass
class FixtureResult:
    date: str
    home_name: str
    away_name: str
    home_goals: int
    away_goals: int
    is_home_for_ref_team: bool


@dataclass
class TeamForm:
    form_string: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    avg_goals_for: float
    avg_goals_against: float
    fixtures: List[FixtureResult] = field(default_factory=list)


@dataclass
class HeadToHead:
    matches: List[FixtureResult]
    summary_text: str
    btts_pct: Optional[float] = None
    over_2_5_pct: Optional[float] = None


class MatchDataProvider(Protocol):
    """Contract a football data source must satisfy to feed MatchAnalyzer."""

    async def find_team(self, name: str) -> Optional[TeamRef]:
        ...

    async def get_league_context(self, team_id: int, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        ...

    async def get_recent_form(
        self, team_id: int, last: int = 5
    ) -> TeamForm:
        ...

    async def get_head_to_head(self, home_id: int, away_id: int, last: int = 5) -> HeadToHead:
        ...

    async def get_injuries(self, team_id: int, season: int) -> List[Dict[str, Any]]:
        ...


def derive_form(team_id: int, fixtures: List[Dict[str, Any]]) -> TeamForm:
    """Derive form (W/D/L string, goal tallies) from a provider-agnostic
    list of fixture dicts: {date, home_id, home_name, away_id, away_name,
    home_goals, away_goals}. Shared by every provider's raw-fixture parsing
    so "form" means the same thing regardless of data source."""
    form_letters = []
    wins = draws = losses = 0
    goals_for = goals_against = 0
    results: List[FixtureResult] = []

    for fx in fixtures:
        is_home = fx.get("home_id") == team_id
        gf = fx["home_goals"] if is_home else fx["away_goals"]
        ga = fx["away_goals"] if is_home else fx["home_goals"]

        goals_for += gf
        goals_against += ga

        if gf > ga:
            form_letters.append("W")
            wins += 1
        elif gf < ga:
            form_letters.append("L")
            losses += 1
        else:
            form_letters.append("D")
            draws += 1

        results.append(FixtureResult(
            date=fx.get("date", ""),
            home_name=fx.get("home_name", "Local"),
            away_name=fx.get("away_name", "Visitante"),
            home_goals=fx.get("home_goals", 0),
            away_goals=fx.get("away_goals", 0),
            is_home_for_ref_team=is_home,
        ))

    played = len(fixtures)
    return TeamForm(
        form_string="".join(form_letters),
        played=played,
        wins=wins,
        draws=draws,
        losses=losses,
        goals_for=goals_for,
        goals_against=goals_against,
        avg_goals_for=round(goals_for / played, 2) if played else 0.0,
        avg_goals_against=round(goals_against / played, 2) if played else 0.0,
        fixtures=results,
    )


def _rest_days(form: TeamForm) -> Optional[int]:
    """Real days since a team's most recent fixture, or None if there's no
    recent fixture to compute it from. Shared by every provider so
    "days of rest" is calculated the same way regardless of data source."""
    if not form.fixtures:
        return None
    try:
        last_date = form.fixtures[-1].date
        played_at = datetime.fromisoformat(last_date.replace("Z", "+00:00"))
        delta = datetime.now(played_at.tzinfo) - played_at
        return max(delta.days, 0)
    except (ValueError, TypeError):
        return None


def build_match_data(
    home_ref: TeamRef,
    away_ref: TeamRef,
    league_name: Optional[str],
    home_form: TeamForm,
    away_form: TeamForm,
    h2h: HeadToHead,
    home_injuries: List[Dict[str, Any]],
    away_injuries: List[Dict[str, Any]],
    home_standing: Optional[Dict[str, Any]] = None,
    away_standing: Optional[Dict[str, Any]] = None,
    stadium: Optional[str] = None,
    source: str = "api_football",
) -> Dict[str, Any]:
    """
    Assemble the match_data dict that feeds PromptEngine, from real data
    only - no fabricated placeholders. Shared by every MatchDataProvider
    implementation so the pipeline downstream (prompt_engine, formatters)
    doesn't need to know which source produced the data.
    """
    return {
        "home_team": home_ref.name,
        "away_team": away_ref.name,
        "league_name": league_name,
        "match_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stadium": stadium or "Estadio",
        "data_source": source,

        "home_position": home_standing.get("position") if home_standing else None,
        "home_points": home_standing.get("points") if home_standing else None,
        "home_played": home_standing.get("played") if home_standing else None,
        "home_form": home_form.form_string,
        "home_goals_for": home_form.goals_for,
        "home_goals_against": home_form.goals_against,
        "home_avg_goals_for": home_form.avg_goals_for,
        "home_avg_goals_against": home_form.avg_goals_against,
        "home_rest_days": _rest_days(home_form),
        "home_injuries": home_injuries,

        "away_position": away_standing.get("position") if away_standing else None,
        "away_points": away_standing.get("points") if away_standing else None,
        "away_played": away_standing.get("played") if away_standing else None,
        "away_form": away_form.form_string,
        "away_goals_for": away_form.goals_for,
        "away_goals_against": away_form.goals_against,
        "away_avg_goals_for": away_form.avg_goals_for,
        "away_avg_goals_against": away_form.avg_goals_against,
        "away_rest_days": _rest_days(away_form),
        "away_injuries": away_injuries,

        "head_to_head": h2h.summary_text,
        "h2h_structured": asdict(h2h),
    }
