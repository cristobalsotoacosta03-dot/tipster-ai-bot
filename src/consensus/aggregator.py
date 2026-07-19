"""
Aggregates per-channel TipperSignals into a single anonymous consensus
summary for a match. Never names which channel said what - only counts.

Integration note (not wired yet): once real channels are configured and
validated, `build_consensus_summary(...).summary_text` is the one string
that would be safe to drop into src/analyzer/prompt_engine.py's templates
as extra context (e.g. a new `$consensus_signal` placeholder) - it's
already stripped of any per-tipster attribution or literal quotes.
"""
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional

from src.consensus.signal_detector import (
    DIRECTION_AWAY,
    DIRECTION_HOME,
    TipperSignal,
)

_DIRECTION_LABELS = {
    DIRECTION_HOME: "el local",
    DIRECTION_AWAY: "el visitante",
    "over": "over 2.5",
    "under": "under 2.5",
    "btts_yes": "ambos marcan",
    "btts_no": "no ambos marcan",
}


@dataclass
class ConsensusResult:
    total_signals: int
    summary_text: str
    winning_direction: Optional[str] = None
    winning_count: int = 0


def build_consensus_summary(
    signals: List[TipperSignal],
    home_team: str,
    away_team: str,
    min_signals: int = 3,
) -> ConsensusResult:
    """
    Turn a list of per-channel signals (already extracted by
    signal_detector.detect_signal, one per channel that mentioned this
    match) into a single aggregate summary.

    Requires at least `min_signals` channels with a usable signal before
    claiming any consensus - below that, a "few tipsters" result would be
    more noise than signal.
    """
    directions = [s.direction for s in signals if s.direction]
    total = len(directions)

    if total < min_signals:
        return ConsensusResult(
            total_signals=total,
            summary_text=f"Señal insuficiente ({total} tipster(s) monitorizados con pick para este partido).",
        )

    counts = Counter(directions)
    winning_direction, winning_count = counts.most_common(1)[0]

    label = _DIRECTION_LABELS.get(winning_direction, winning_direction)
    team_label = {
        DIRECTION_HOME: home_team,
        DIRECTION_AWAY: away_team,
    }.get(winning_direction, label)

    if winning_direction in (DIRECTION_HOME, DIRECTION_AWAY):
        summary_text = f"{winning_count} de {total} tipsters monitorizados favorecen a {team_label}."
    else:
        summary_text = f"{winning_count} de {total} tipsters monitorizados favorecen '{label}'."

    return ConsensusResult(
        total_signals=total,
        summary_text=summary_text,
        winning_direction=winning_direction,
        winning_count=winning_count,
    )
