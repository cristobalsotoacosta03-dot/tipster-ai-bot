"""
Tests for ClaudeClient. No real network calls: the Anthropic SDK client is
mocked out entirely.
"""
import re
from unittest.mock import AsyncMock, MagicMock, patch
import anthropic
import pytest
import tenacity

from src.analyzer.claude_client import ClaudeClient


def make_message(text: str):
    message = MagicMock()
    message.content = [MagicMock(text=text)]
    return message


@pytest.fixture
def client_enabled():
    with patch("src.analyzer.claude_client.settings") as mock_settings:
        mock_settings.anthropic_api_key = "sk-ant-dummy"
        client = ClaudeClient()
        client.client = AsyncMock()
        return client


@pytest.fixture
def client_disabled():
    with patch("src.analyzer.claude_client.settings") as mock_settings:
        mock_settings.anthropic_api_key = None
        return ClaudeClient()


class TestSystemPrompt:
    def test_default_system_prompt_has_no_stray_non_latin_characters(self, client_enabled):
        """Regression test for a corrupted prompt that shipped to production
        with CJK characters mixed into Spanish text ("构建ción de juego")."""
        prompt = client_enabled._get_default_system_prompt()
        assert not re.search(r"[一-鿿]", prompt)
        assert "construcción de juego" in prompt


class TestAnalyzeMatch:
    @pytest.mark.asyncio
    async def test_disabled_client_returns_none_without_calling_api(self, client_disabled):
        result = await client_disabled.analyze_match("some prompt")
        assert result is None

    @pytest.mark.asyncio
    async def test_sends_prompt_and_returns_response_text(self, client_enabled):
        client_enabled.client.messages.create = AsyncMock(
            return_value=make_message("Análisis generado.")
        )

        result = await client_enabled.analyze_match("Analiza este partido")

        assert result == "Análisis generado."
        client_enabled.client.messages.create.assert_awaited_once()
        _, kwargs = client_enabled.client.messages.create.call_args
        assert kwargs["model"] == client_enabled.model
        assert kwargs["messages"][0]["content"] == "Analiza este partido"

    @pytest.mark.asyncio
    async def test_uses_default_system_prompt_when_none_given(self, client_enabled):
        client_enabled.client.messages.create = AsyncMock(return_value=make_message("ok"))

        await client_enabled.analyze_match("prompt")

        _, kwargs = client_enabled.client.messages.create.call_args
        assert kwargs["system"] == client_enabled._get_default_system_prompt()

    @pytest.mark.asyncio
    async def test_custom_system_prompt_is_respected(self, client_enabled):
        client_enabled.client.messages.create = AsyncMock(return_value=make_message("ok"))

        await client_enabled.analyze_match("prompt", system_prompt="custom system")

        _, kwargs = client_enabled.client.messages.create.call_args
        assert kwargs["system"] == "custom system"

    @pytest.mark.asyncio
    async def test_rate_limit_error_propagates_after_retries(self, client_enabled, monkeypatch):
        # Skip the real exponential backoff (2-10s per attempt x 3 attempts)
        # so this test doesn't stall the suite.
        monkeypatch.setattr(ClaudeClient.analyze_match.retry, "wait", tenacity.wait_none())

        error = anthropic.RateLimitError(
            "rate limited", response=MagicMock(status_code=429, headers={}), body=None
        )
        client_enabled.client.messages.create = AsyncMock(side_effect=error)

        with pytest.raises(tenacity.RetryError):
            await client_enabled.analyze_match("prompt")

        assert client_enabled.client.messages.create.await_count == 3  # stop_after_attempt(3)

    @pytest.mark.asyncio
    async def test_unexpected_error_propagates(self, client_enabled):
        client_enabled.client.messages.create = AsyncMock(side_effect=RuntimeError("boom"))

        with pytest.raises(RuntimeError):
            await client_enabled.analyze_match("prompt")


class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_disabled_client_health_check_is_false(self, client_disabled):
        assert await client_disabled.health_check() is False

    @pytest.mark.asyncio
    async def test_enabled_client_health_check_true_on_response(self, client_enabled):
        client_enabled.client.messages.create = AsyncMock(return_value=make_message("Hi"))
        assert await client_enabled.health_check() is True

    @pytest.mark.asyncio
    async def test_enabled_client_health_check_false_on_error(self, client_enabled):
        client_enabled.client.messages.create = AsyncMock(side_effect=RuntimeError("down"))
        assert await client_enabled.health_check() is False
