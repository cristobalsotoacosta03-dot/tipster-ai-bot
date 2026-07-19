"""
Tests for the (inactive) tipster-consensus module: signal extraction,
aggregation, and channel reading with a mocked Telethon-like client.
No real Telegram/Telethon connection is made anywhere in this file.
"""
import pytest

from src.consensus.signal_detector import detect_signal, TipperSignal
from src.consensus.aggregator import build_consensus_summary
from src.consensus.channel_reader import read_recent_messages, ChannelMessage


class TestDetectSignal:
    def test_home_favorite_detected(self):
        signal = detect_signal(
            "El Real Madrid gana en casa sin problemas", "Real Madrid", "Barcelona"
        )
        assert signal.direction == "home"

    def test_away_favorite_detected(self):
        signal = detect_signal(
            "Creo que el Barcelona gana fuera hoy", "Real Madrid", "Barcelona"
        )
        assert signal.direction == "away"

    def test_over_detected(self):
        signal = detect_signal(
            "Real Madrid vs Barcelona - mas de 2.5 goles claro", "Real Madrid", "Barcelona"
        )
        assert signal.direction == "over"

    def test_btts_yes_detected(self):
        signal = detect_signal(
            "Real Madrid vs Barcelona: ambos marcan hoy", "Real Madrid", "Barcelona"
        )
        assert signal.direction == "btts_yes"

    def test_confidence_extracted(self):
        signal = detect_signal(
            "Real Madrid gana en casa, 80% de confianza", "Real Madrid", "Barcelona"
        )
        assert signal.confidence_pct == 80

    def test_accents_normalized(self):
        signal = detect_signal(
            "El Atlético gana en casa", "Atletico Madrid", "Sevilla"
        )
        assert signal is not None

    def test_unrelated_match_returns_none(self):
        signal = detect_signal(
            "El Valencia gana en casa hoy", "Real Madrid", "Barcelona"
        )
        assert signal is None

    def test_empty_message_returns_none(self):
        assert detect_signal("", "Real Madrid", "Barcelona") is None

    def test_bare_mention_leans_towards_team(self):
        signal = detect_signal(
            "Ojo al Real Madrid esta noche", "Real Madrid", "Barcelona"
        )
        assert signal.direction == "home"

    def test_does_not_leak_original_text(self):
        signal = detect_signal(
            "El Real Madrid gana en casa, texto muy especifico del canal",
            "Real Madrid",
            "Barcelona",
        )
        assert not hasattr(signal, "text")
        assert not hasattr(signal, "message_text")


class TestBuildConsensusSummary:
    def test_insufficient_signals(self):
        signals = [TipperSignal(direction="home"), TipperSignal(direction="home")]
        result = build_consensus_summary(signals, "Real Madrid", "Barcelona", min_signals=3)
        assert "insuficiente" in result.summary_text.lower()
        assert result.winning_direction is None

    def test_home_consensus(self):
        signals = [
            TipperSignal(direction="home"),
            TipperSignal(direction="home"),
            TipperSignal(direction="home"),
            TipperSignal(direction="away"),
        ]
        result = build_consensus_summary(signals, "Real Madrid", "Barcelona", min_signals=3)
        assert result.winning_direction == "home"
        assert result.winning_count == 3
        assert result.total_signals == 4
        assert "Real Madrid" in result.summary_text
        # Never attributes the pick to a specific channel/tipster.
        assert "canal" not in result.summary_text.lower()

    def test_non_team_direction_consensus(self):
        signals = [
            TipperSignal(direction="over"),
            TipperSignal(direction="over"),
            TipperSignal(direction="over"),
        ]
        result = build_consensus_summary(signals, "Real Madrid", "Barcelona", min_signals=3)
        assert result.winning_direction == "over"
        assert "over 2.5" in result.summary_text

    def test_signals_without_direction_are_excluded(self):
        signals = [TipperSignal(direction=None), TipperSignal(direction=None)]
        result = build_consensus_summary(signals, "Real Madrid", "Barcelona", min_signals=1)
        assert result.total_signals == 0


class FakeTelegramClient:
    """Minimal stand-in for telethon.TelegramClient's async interface."""

    def __init__(self, messages_by_channel):
        self._messages_by_channel = messages_by_channel

    async def get_messages(self, entity, limit):
        if entity == "broken_channel":
            raise RuntimeError("channel is private")
        return self._messages_by_channel.get(entity, [])[:limit]


class FakeMessage:
    def __init__(self, text):
        self.text = text


class TestReadRecentMessages:
    @pytest.mark.asyncio
    async def test_reads_messages_from_multiple_channels(self):
        client = FakeTelegramClient({
            "tipster_a": [FakeMessage("Real Madrid gana en casa")],
            "tipster_b": [FakeMessage("Barcelona gana fuera")],
        })
        messages = await read_recent_messages(client, ["tipster_a", "tipster_b"])
        assert len(messages) == 2
        assert ChannelMessage(channel="tipster_a", text="Real Madrid gana en casa") in messages

    @pytest.mark.asyncio
    async def test_broken_channel_is_skipped_not_fatal(self):
        client = FakeTelegramClient({
            "tipster_a": [FakeMessage("Real Madrid gana en casa")],
        })
        messages = await read_recent_messages(client, ["broken_channel", "tipster_a"])
        assert len(messages) == 1
        assert messages[0].channel == "tipster_a"

    @pytest.mark.asyncio
    async def test_empty_channel_list_returns_empty(self):
        client = FakeTelegramClient({})
        messages = await read_recent_messages(client, [])
        assert messages == []
