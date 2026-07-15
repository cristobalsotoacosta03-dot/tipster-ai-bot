"""
Response Formatters for Telegram.
Specializes in formatting analysis results with a "Preferente player" style
while maintaining commercial hooks for VIP conversion.
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AnalysisFormatter:
    """
    Formats match analysis for Telegram with a distinctive style:
    - Language of a "Preferente" player (practical, direct, experienced)
    - Tactical breakdown that reflects real game reading
    - Commercial hooks for VIP conversion
    """
    
    def __init__(self):
        """Initialize formatter."""
        self.max_message_length = 4096  # Telegram limit
        logger.info("Analysis Formatter initialized")
    
    def format_analysis_for_telegram(
        self,
        analysis_result: Dict[str, Any],
        user_is_vip: bool = False
    ) -> str:
        """
        Format analysis result for Telegram with Preferente-style language.
        
        Args:
            analysis_result: Complete analysis from MatchAnalyzer
            user_is_vip: Whether user has VIP access
            
        Returns:
            Formatted message string
        """
        try:
            analysis_text = analysis_result.get("analysis", "")
            match_data = analysis_result.get("match_data", {})
            analysis_type = analysis_result.get("analysis_type", "full")
            
            # For VIP users, return the full analysis
            if user_is_vip and analysis_type == "premium":
                return self._format_premium_analysis(analysis_result)
            
            # For free users or express, format with commercial hooks
            formatted = self._format_with_commercial_hooks(
                analysis_text,
                match_data,
                analysis_type,
                user_is_vip
            )
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting analysis: {e}", exc_info=True)
            return "❌ Error al formatear el análisis. Por favor, inténtalo de nuevo."
    
    def _format_with_commercial_hooks(
        self,
        analysis_text: str,
        match_data: Dict[str, Any],
        analysis_type: str,
        user_is_vip: bool
    ) -> str:
        """
        Format analysis with Preferente-style language and VIP hooks.
        
        Args:
            analysis_text: Raw analysis from Claude
            match_data: Match data dictionary
            analysis_type: Type of analysis
            user_is_vip: Whether user has VIP access
            
        Returns:
            Formatted message with hooks
        """
        home_team = match_data.get("home_team", "Local")
        away_team = match_data.get("away_team", "Visitante")
        
        # Header with match info
        header = f"⚽ ANÁLISIS: {home_team} vs {away_team}\n"
        header += "─" * 35 + "\n\n"
        
        # Extract key insights from analysis (first 1500 chars for free users)
        if analysis_type == "express":
            # Express: condensed version
            tactical_summary = self._extract_tactical_summary(analysis_text)
            formatted_analysis = f"🎯 **Vistazo rápido:**\n{tactical_summary}\n\n"
        else:
            # Full: more detail but still limited for free users
            formatted_analysis = self._format_full_analysis_free(analysis_text)
        
        # Add Preferente-style reading
        preferente_insight = self._generate_preferente_insight(match_data)
        
        # Commercial hook for VIP
        vip_hook = self._generate_vip_hook(match_data, analysis_type)
        
        # Combine all parts
        complete_message = header + formatted_analysis + "\n" + preferente_insight + "\n" + vip_hook
        
        # Ensure we don't exceed Telegram limit
        if len(complete_message) > self.max_message_length:
            complete_message = complete_message[:self.max_message_length - 100]
            complete_message += "\n\n... (continúa en VIP)"
        
        return complete_message
    
    def _extract_tactical_summary(self, analysis_text: str) -> str:
        """Extract tactical summary from full analysis."""
        # Extract key sections
        lines = analysis_text.split('\n')
        summary_lines = []
        
        for line in lines:
            # Look for key tactical indicators
            if any(keyword in line.lower() for keyword in [
                'pressing', 'ppda', 'fatiga', 'ventaja', 'pronóstico',
                'stake', 'confianza', 'táctico', 'físico'
            ]):
                summary_lines.append(line)
            
            if len(summary_lines) >= 8:
                break
        
        return '\n'.join(summary_lines) if summary_lines else analysis_text[:500]
    
    def _format_full_analysis_free(self, analysis_text: str) -> str:
        """Format full analysis for free users (truncated)."""
        # Take first 1200 characters
        truncated = analysis_text[:1200]
        
        # Add ellipsis if truncated
        if len(analysis_text) > 1200:
            truncated += "..."
        
        return truncated
    
    def _generate_preferente_insight(self, match_data: Dict[str, Any]) -> str:
        """
        Generate insight in the style of a Preferente player.
        Direct, practical, experienced voice.
        """
        home_team = match_data.get("home_team", "Local")
        away_team = match_data.get("away_team", "Visitante")
        
        # Get key metrics
        home_xg = match_data.get("home_xg", 1.5)
        away_xg = match_data.get("away_xg", 1.5)
        home_rest = match_data.get("home_rest_days", 7)
        away_rest = match_data.get("away_rest_days", 7)
        home_ppda = match_data.get("home_ppda", 10)
        away_ppda = match_data.get("away_ppda", 10)
        
        # Generate insights based on data
        insights = []
        
        # Physical advantage
        if abs(home_rest - away_rest) >= 2:
            if home_rest > away_rest:
                insights.append(f"💪 Ojo aquí: el {home_team} llega más fresco. {home_rest - away_rest} días más de descanso se nota en el minuto 70.")
            else:
                insights.append(f"⚡ Cuidado: el {away_team} viene con más descanso. Eso es ventaja en la fase final.")
        
        # Pressing advantage
        if abs(home_ppda - away_ppda) > 3:
            if home_ppda < away_ppda:
                insights.append(f"🔥 El {home_team} presiona más. Va a recuperar arriba y generar ocasiones.")
            else:
                insights.append(f"🛡️ El {away_team} deja jugar. Si el {home_team} no aprovecha, lo va a sufrir en las contras.")
        
        # xG differential
        xg_diff = home_xg - away_xg
        if abs(xg_diff) > 0.4:
            if xg_diff > 0:
                insights.append(f"📊 Los números no mienten: el {home_team} genera más peligro. {home_xg:.2f} xG vs {away_xg:.2f} xG.")
            else:
                insights.append(f"📊 Ojo con el {away_team}: {away_xg:.2f} xG es muy buena cifra para ser visitante.")
        
        # Default insight if no clear advantage
        if not insights:
            insights.append("🎯 Partido igualado. Los detalles decidirán: set pieces, concentración, y quién quiera más.")
        
        # Format as Preferente-style insight
        insight_text = "\n".join(insights)
        
        return f"━━━━━━━━━━━━━━━━━━━━\n📝 **Lo que ve un jugador de Preferente:**\n\n{insight_text}\n━━━━━━━━━━━━━━━━━━━━"
    
    def _generate_vip_hook(self, match_data: Dict[str, Any], analysis_type: str) -> str:
        """
        Generate commercial hook for VIP conversion.
        Creates urgency and shows value of detailed analysis.
        """
        home_team = match_data.get("home_team", "Local")
        away_team = match_data.get("away_team", "Visitante")
        
        # Different hooks based on analysis type
        if analysis_type == "express":
            hook = f"""
⭐ **¿Quieres el análisis COMPLETO?**

En la versión VIP tienes:
✅ Análisis táctico PROFUNDO (sistemas de juego, pressing, transiciones)
✅ Justificación técnica DETALLADA de cada pronóstico
✅ Stake recomendado (1-5 unidades) con razonamiento
✅ Factores de riesgo específicos
✅ Alternativas y combinadas sugeridas
✅ Seguimiento en vivo durante el partido

🎯 **Stake del día:** 3/5 unidades
💰 **Inversión:** €29.99/mes

💬 [Suscribirse al VIP] o contacta con @TuSoporte
"""
        else:
            # Full analysis hook - tease more depth
            hook = f"""
━━━━━━━━━━━━━━━━━━━━

🔒 **ANÁLISIS PREMIUM DISPONIBLE**

Este es un vistazo. El análisis VIP incluye:

🧠 **Análisis Táctico-Profesional:**
• Sistemas de juego probables (4-3-3, 4-2-3-1, etc.)
• Estrategia de pressing y bloque defensivo
• Claves tácticas del partido

📈 **Métricas Avanzadas Interpretadas:**
• xG, PPDA, progresión ofensiva
• Eficiencia en finalización
• Set pieces como factor decisivo

⚠️ **Factores de Riesgo Detallados:**
• Lesiones y su impacto real
• Fatiga acumulada (sprints, rotaciones)
• Presión y motivación

💰 **PRONÓSTICO VIP:**
• Mercado recomendado con JUSTIFICACIÓN TÉCNICA
• Stake: X/5 unidades
• Confianza: X%
• Alternativas y combinadas

📊 **Seguimiento en vivo** durante el partido

💎 **Acceso al grupo VIP** con análisis diarios

🎯 **Tu inversión:** €29.99/mes o €299/año (ahorra 2 meses)

📩 Contacta con @TuSoporte para suscribirte
"""
        
        return hook
    
    def _format_premium_analysis(self, analysis_result: Dict[str, Any]) -> str:
        """Format premium analysis for VIP users."""
        analysis_text = analysis_result.get("analysis", "")
        
        # Add VIP badge
        vip_header = "👑 **ANÁLISIS PREMIUM - VIP**\n"
        vip_header += "═" * 35 + "\n\n"
        
        # Add the full analysis
        formatted = vip_header + analysis_text
        
        # Add VIP footer
        vip_footer = "\n\n" + "═" * 35
        vip_footer += "\n✅ **Acceso VIP activo**"
        vip_footer += "\n📊 Próximo análisis: Mañana 10:00"
        vip_footer += "\n💬 Grupo VIP: @TipsterIA_VIP"
        
        return formatted + vip_footer
    
    def format_error(self, error_type: str = "general") -> str:
        """Format error message."""
        errors = {
            "general": "❌ Error al procesar el análisis. Por favor, inténtalo de nuevo.",
            "api_error": "⚠️ Servicio temporalmente no disponible. Intenta en 2 minutos.",
            "limit_reached": "🚫 Has alcanzado el límite de análisis gratuitos de hoy.",
            "invalid_teams": "⚠️ No pude encontrar uno o ambos equipos. Verifica los nombres.",
            "no_data": "📊 Datos no disponibles para este partido. Prueba con otro encuentro.",
        }
        
        return errors.get(error_type, errors["general"])
    
    def format_limit_message(self, analyses_used: int, limit: int) -> str:
        """Format message when user reaches limit."""
        return f"""
⚠️ **Límite de análisis gratuitos alcanzado**

Has usado {analyses_used}/{limit} análisis gratuitos hoy.

**Para continuar:**
💎 Suscríbete al VIP y obtén análisis ILIMITADOS
📊 Acceso a análisis premium diarios
🎯 Grupo exclusivo con seguimiento en vivo

💰 **€29.99/mes** - Cancela cuando quieras

Contacta con @TuSoporte
"""
    
    def format_success_message(self, analysis_type: str) -> str:
        """Format success message after analysis."""
        messages = {
            "express": "✅ Análisis rápido enviado. Para más detalle, suscríbete al VIP.",
            "full": "✅ Análisis completo enviado. En VIP tienes aún más profundidad.",
            "premium": "✅ Análisis premium enviado. Disfruta del contenido exclusivo."
        }
        
        return messages.get(analysis_type, messages["full"])


class MessageBuilder:
    """
    Builds complex Telegram messages with inline keyboards.
    """
    
    @staticmethod
    def build_vip_promo_keyboard() -> Dict[str, Any]:
        """Build inline keyboard for VIP promotion."""
        return {
            "inline_keyboard": [
                [
                    {
                        "text": "💎 Suscribirse al VIP (€29.99/mes)",
                        "callback_data": "vip_subscribe_monthly"
                    }
                ],
                [
                    {
                        "text": "📆 Plan Anual (€299 - Ahorra 2 meses)",
                        "callback_data": "vip_subscribe_yearly"
                    }
                ],
                [
                    {
                        "text": "📞 Contactar Soporte",
                        "url": "https://t.me/TuSoporte"
                    }
                ]
            ]
        }
    
    @staticmethod
    def build_analysis_keyboard(match_id: str, has_vip: bool) -> Dict[str, Any]:
        """Build inline keyboard for analysis results."""
        keyboard = [
            [
                {
                    "text": "🔄 Actualizar análisis",
                    "callback_data": f"refresh_analysis:{match_id}"
                }
            ]
        ]
        
        if not has_vip:
            keyboard.append([
                {
                    "text": "⭐ Ver análisis VIP",
                    "callback_data": f"vip_promo:{match_id}"
                }
            ])
        
        return {"inline_keyboard": keyboard}