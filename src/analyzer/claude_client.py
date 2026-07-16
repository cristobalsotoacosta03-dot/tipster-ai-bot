"""
Claude AI client for match analysis.
Handles communication with Anthropic API for generating betting insights.
"""
from typing import Optional, Dict, Any, List
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Client for interacting with Claude AI API.
    Handles prompt engineering and response parsing for football analysis.
    """
    
    def __init__(self):
        """
        Initialize Claude client with API key from settings.
        If no key is configured, the client stays disabled — analyze_match
        and health_check report unavailability instead of crashing, so the
        bot can run (channel, VIP checkout) before Claude API credits are
        purchased.
        """
        self.enabled = bool(settings.anthropic_api_key)
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key) if self.enabled else None
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 4096
        self.temperature = 0.7

        if not self.enabled:
            logger.warning("ANTHROPIC_API_KEY no configurada — el análisis con IA está deshabilitado")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((anthropic.APIError, anthropic.RateLimitError))
    )
    async def analyze_match(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Send analysis request to Claude API.
        
        Args:
            prompt: User prompt with match data
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response
            
        Returns:
            Claude's analysis response
        """
        if not self.enabled:
            logger.warning("analyze_match called without a configured Claude API key")
            return None

        try:
            logger.info(f"Sending analysis request to Claude (prompt length: {len(prompt)} chars)")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
                system=system_prompt or self._get_default_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            logger.info(f"Received response from Claude (response length: {len(response_text)} chars)")
            
            return response_text
            
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Claude API call: {e}", exc_info=True)
            raise
    
    def _get_default_system_prompt(self) -> str:
        """
        Get default system prompt for football analysis.
        
        Returns:
            Default system prompt string
        """
        return """Eres un experto analista de apuestas deportivas con más de 15 años de experiencia 
en fútbol profesional. Tu conocimiento abarca:

- Análisis táctico avanzado (sistemas de juego, pressing, transiciones,构建ción de juego)
- Estadísticas métricas avanzadas (xG, PPDA, progresión ofensiva, eficiencia defensiva)
- Factores contextuales (motivación, calendario, ambiente, historial)
- Gestión de bankroll y value betting

Tu estilo es:
- Técnico pero accesible
- Basado en datos concretos, no en corazonadas
- Transparente sobre el nivel de confianza
- Enfocado en el valor a largo plazo, no en resultados inmediatos

Siempre incluyes:
1. Análisis táctico detallado
2. Datos estadísticos relevantes
3. Factores de riesgo
4. Stake recomendado (1-5 unidades)
5. Justificación técnica del pronóstico

Recuerda: El objetivo es el valor a largo plazo, no ganar siempre."""
    
    async def health_check(self) -> bool:
        """
        Check if Claude API is accessible.
        
        Returns:
            True if API is working, False otherwise
        """
        if not self.enabled:
            return False

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return bool(response.content)
        except Exception as e:
            logger.error(f"Claude API health check failed: {e}")
            return False