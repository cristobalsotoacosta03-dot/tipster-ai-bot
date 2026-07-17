"""
Advanced Prompt Engine for football match analysis.
Builds prompts from real data (fixtures, standings, head-to-head, injuries)
and is explicit with Claude/the user when a metric isn't available, instead
of substituting a plausible-looking fabricated number.
"""
from typing import Dict, Any, List, Optional
from string import Template
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

NOT_AVAILABLE = "No disponible (dato no proporcionado por el plan gratuito de datos)"


class PromptEngine:
    """
    Advanced prompt generation system for football analysis.
    Focuses on the tactical/physical/statistical signals we can actually
    back with real match data, and says so plainly when a signal is missing.
    """

    def __init__(self):
        """Initialize prompt engine with templates."""
        self.templates = self._load_templates()
        logger.info("Prompt Engine initialized with tactical focus")

    def _load_templates(self) -> Dict[str, Template]:
        """Load all prompt templates."""
        return {
            "full_analysis": Template(self._get_full_analysis_template()),
            "express": Template(self._get_express_template()),
            "premium": Template(self._get_premium_template()),
        }

    def _get_full_analysis_template(self) -> str:
        """
        Full analysis template with deep tactical focus.
        Emphasizes variables that actually decide matches.
        """
        return """# ANÁLISIS TÁCTICO-PROFESIONAL DE PARTIDO

## 🧠 CONTEXTO ESTRATÉGICO

**Partido:** $home_team vs $away_team
**Competición:** $league_name

**Momento de la temporada:**
- Posición $home_team: $home_position° ($home_points pts, $home_played PJ)
- Posición $away_team: $away_position° ($away_points pts, $away_played PJ)

---

## ⚽ FORMA REAL Y RENDIMIENTO RECIENTE

### $home_team
**Forma últimos partidos:** $home_form
**Goles a favor / en contra (últimos partidos):** $home_goals_for / $home_goals_against ($home_avg_goals_for de media a favor, $home_avg_goals_against en contra)

**Puntos fuertes detectables:**
$home_strengths

**Puntos débiles explotables:**
$home_weaknesses

### $away_team
**Forma últimos partidos:** $away_form
**Goles a favor / en contra (últimos partidos):** $away_goals_for / $away_goals_against ($away_avg_goals_for de media a favor, $away_avg_goals_against en contra)

**Puntos fuertes detectables:**
$away_strengths

**Puntos débiles explotables:**
$away_weaknesses

---

## 📊 MÉTRICAS AVANZADAS

*Nota: xG, PPDA, posesión y métricas físicas no están disponibles en el plan gratuito de datos actual y no se incluyen para no inventar cifras.*

### Diferencial ofensivo (basado en goles reales)
$goal_differential_analysis

### Fatiga y Descanso
- **Días de descanso reales:** $home_rest_days vs $away_rest_days
  - *Ventaja/desventaja física*

---

## ⚠️ FACTORES DECISIVOS

### Lesiones y Sanciones (IMPACTO DIRECTO)
**$home_team:**
$home_injuries_analysis

**$away_team:**
$away_injuries_analysis

**Análisis de impacto:**
- Jugadores clave fuera: $key_players_out
- Nivel de impacto: $injury_impact_level (Alto/Medio/Bajo)

---

## 💰 MERCADO DE CUOTAS (Datos Reales)

$market_odds_summary

---

## 🎯 CONFRONTACIÓN DIRECTA

### Historial Reciente
**Últimos enfrentamientos:**
$head_to_head

**Patrones identificados:**
- $home_team gana cuando: $home_win_conditions
- $away_team gana cuando: $away_win_conditions
- Patrón recurrente: $recurring_pattern

---

## 📋 INSTRUCCIONES DE ANÁLISIS

### 1. ANÁLISIS DE FORMA Y RENDIMIENTO (Obligatorio)
Analiza la forma reciente real de ambos equipos (resultados y goles, no estadísticas inventadas):

- **¿Quién llega en mejor momento?**
  - Compara forma reciente y balance de goles
- **¿Dónde se decidirá el partido?**
  - Con los datos disponibles, ¿hay una ventaja ofensiva o defensiva clara?
- **Ventaja detectable:** $tactical_advantage

### 2. ANÁLISIS FÍSICO (Obligatorio, con los datos disponibles)
- **¿Quién llega más fresco?** Compara días de descanso reales.
- **Ventaja física:** $physical_advantage

### 3. FACTORES DE LESIONES (Obligatorio)
- **Historial reciente:** $recent_form_impact

### 4. PRONÓSTICO (Obligatorio - Con Justificación Técnica)

Si hay cuotas de mercado reales disponibles arriba, compara tu propia estimación con la
probabilidad implícita del mercado y dilo explícitamente (¿hay valor aparente o el mercado ya
lo refleja?). Si no hay cuotas disponibles, no asumas ninguna.

**Mercado recomendado:** $recommended_market

**Stake recomendado:** $stake/5 unidades

**Nivel de confianza:** $confidence_level%

**Justificación técnica (OBLIGATORIA, basada solo en datos reales):**
$technical_justification

**Factores clave que soportan el pronóstico:**
1. $factor_1
2. $factor_2
3. $factor_3

**Factores de riesgo:**
$risk_factors

### 5. ALTERNATIVAS (Opcional pero Valioso)
- Mercado secundario: $alternative_market_1

---

## ⚠️ REGLAS CRÍTICAS

1. **NO hagas predicciones basadas en estadísticas vacías** - Interpreta el contexto
2. **SIEMPRE justifica técnicamente** - Cada pronóstico necesita argumentos sólidos
3. **Si un dato dice "No disponible", NO lo inventes ni lo asumas** - trabaja solo con lo que hay
4. **Si no hay valor claro, DILO** - Mejor no analizar que dar pronósticos sin fundamento
5. **TRANSPARENCIA total** - Muestra tu nivel de confianza real

---

## 📊 RESUMEN EJECUTIVO (Para el usuario)

### 🎯 Pronóstico Principal
**Mercado:** $recommended_market
**Stake:** $stake/5 unidades
**Confianza:** $confidence_level%

### 💡 Por qué este pronóstico
$executive_summary

### ⚠️ Riesgo principal
$main_risk

---

**Recuerda:** Estás analizando para apostadores serios que buscan valor a largo plazo, no para espectadores que quieren emoción. Tu análisis debe reflejar profesionalismo y rigor, basado únicamente en datos reales disponibles."""

    def _get_express_template(self) -> str:
        """
        Express analysis template for quick tips.
        Still tactical but condensed.
        """
        return """⚡ ANÁLISIS RÁPIDO: $home_team vs $away_team

**Contexto:** $league_name

**Ventaja detectable:** $tactical_advantage
**Ventaja física:** $physical_advantage

**Forma reciente:**
- $home_team: $home_form (GF $home_goals_for / GC $home_goals_against)
- $away_team: $away_form (GF $away_goals_for / GC $away_goals_against)

**Fatiga:** $fatigue_advantage

**Mercado:** $market_odds_summary

**Factor decisivo:** $decisive_factor

**Pronóstico:** $recommended_market
**Stake:** $stake/5
**Confianza:** $confidence_level%

$technical_justification"""

    def _get_premium_template(self) -> str:
        """
        Premium analysis template for VIP users.
        Maximum depth with the real signals available.
        """
        return """# 🔍 ANÁLISIS PREMIUM: $home_team vs $away_team

## 📊 Contexto Estratégico
$strategic_context

## 🧠 Análisis de Forma y Rendimiento
$deep_tactical_analysis

## 💪 Análisis Físico y Fatiga
$physical_analysis

## 📈 Métricas Reales Interpretadas
$advanced_metrics_analysis

## 💰 Mercado de Cuotas (Datos Reales)
$market_odds_summary

## ⚠️ Factores de Riesgo Detallados
$detailed_risk_analysis

## 💡 Value Identification
$value_identification

## 🎯 Pronóstico Principal
**Mercado:** $recommended_market
**Stake:** $stake/5 unidades
**Confianza:** $confidence_level%

## 📋 Justificación Técnica Completa
$full_technical_justification

## 🔄 Alternativas
$alternatives_and_combinations"""

    def generate_full_analysis_prompt(self, match_data: Dict[str, Any]) -> str:
        """Generate complete analysis prompt with all available real signals."""
        try:
            enriched_data = self._enrich_with_tactical_analysis(match_data)
            prompt = self.templates["full_analysis"].safe_substitute(**enriched_data)
            logger.info(f"Generated full analysis prompt ({len(prompt)} chars)")
            return prompt
        except Exception as e:
            logger.error(f"Error generating full analysis prompt: {e}", exc_info=True)
            raise

    def generate_express_prompt(self, match_data: Dict[str, Any]) -> str:
        """Generate express analysis prompt for quick tips."""
        try:
            enriched_data = self._enrich_with_tactical_analysis(match_data)
            prompt = self.templates["express"].safe_substitute(**enriched_data)
            logger.info(f"Generated express prompt ({len(prompt)} chars)")
            return prompt
        except Exception as e:
            logger.error(f"Error generating express prompt: {e}", exc_info=True)
            raise

    def generate_premium_prompt(self, match_data: Dict[str, Any]) -> str:
        """Generate premium analysis prompt for VIP users."""
        try:
            enriched_data = self._enrich_with_tactical_analysis(match_data)
            enriched_data.update(self._build_premium_sections(enriched_data))
            prompt = self.templates["premium"].safe_substitute(**enriched_data)
            logger.info(f"Generated premium prompt ({len(prompt)} chars)")
            return prompt
        except Exception as e:
            logger.error(f"Error generating premium prompt: {e}", exc_info=True)
            raise

    def calculate_confidence(self, match_data: Dict[str, Any]) -> int:
        """Public wrapper: confidence level (0-100) for a given match, so
        callers outside the prompt (e.g. the Telegram formatter) can render
        it without duplicating the heuristic."""
        return self._calculate_confidence(match_data)

    def calculate_stake(self, match_data: Dict[str, Any]) -> int:
        """Public wrapper: recommended stake (1-5 units) for a given match."""
        return self._calculate_stake(match_data)

    # ==================== ENRICHMENT ====================

    def _num_or_na(self, value: Any) -> Any:
        """Sanitize a possibly-missing numeric field for template substitution
        so we never leak a Python `None` or a raw `$placeholder` into the text
        sent to Claude/the user."""
        return value if value is not None else "N/D"

    def _enrich_with_tactical_analysis(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich match data with derived analysis text. Every derived value is
        computed from real fields in `match_data`; when the underlying real
        field is missing, the derived text says so instead of guessing.
        """
        enriched = match_data.copy()

        for key in (
            "home_position", "home_points", "home_played",
            "away_position", "away_points", "away_played",
            "home_rest_days", "away_rest_days",
            "home_avg_goals_for", "home_avg_goals_against",
            "away_avg_goals_for", "away_avg_goals_against",
        ):
            enriched[key] = self._num_or_na(match_data.get(key))

        enriched["league_name"] = match_data.get("league_name") or "Liga no identificada"

        h2h = match_data.get("h2h_structured") or {}

        enriched.update({
            # Strengths/weaknesses from real form
            "home_strengths": self._identify_strengths(match_data, "home"),
            "home_weaknesses": self._identify_weaknesses(match_data, "home"),
            "away_strengths": self._identify_strengths(match_data, "away"),
            "away_weaknesses": self._identify_weaknesses(match_data, "away"),

            "goal_differential_analysis": self._goal_differential_analysis(match_data),
            "market_odds_summary": self._market_odds_summary(match_data),
            "fatigue_advantage": self._calculate_fatigue_advantage(match_data),
            "tactical_advantage": self._determine_tactical_advantage(match_data),
            "physical_advantage": self._calculate_fatigue_advantage(match_data),
            "decisive_factor": self._identify_decisive_factor(match_data),
            "recent_form_impact": self._recent_form_impact(match_data),

            # Head-to-head derived text
            "home_win_conditions": self._win_conditions(h2h, match_data.get("home_team", "Local"), for_home=True),
            "away_win_conditions": self._win_conditions(h2h, match_data.get("away_team", "Visitante"), for_home=False),
            "recurring_pattern": self._recurring_pattern(h2h),

            # Injuries
            "home_injuries_analysis": self._analyze_injuries(match_data, "home"),
            "away_injuries_analysis": self._analyze_injuries(match_data, "away"),
            "key_players_out": self._identify_key_players_out(match_data),
            "injury_impact_level": self._assess_injury_impact(match_data),

            # Prediction
            "recommended_market": self._recommend_market(match_data),
            "stake": self._calculate_stake(match_data),
            "confidence_level": self._calculate_confidence(match_data),
            "technical_justification": self._generate_technical_justification(match_data),
            "risk_factors": self._identify_risk_factors(match_data),
            "factor_1": "",
            "factor_2": "",
            "factor_3": "",
            "alternative_market_1": self._alternative_market(match_data),

            # Summary
            "executive_summary": "",
            "main_risk": "",
        })

        enriched = self._generate_dynamic_factors(enriched, match_data)

        return enriched

    def _build_premium_sections(self, enriched: Dict[str, Any]) -> Dict[str, str]:
        """Map already-derived signals onto the premium template's broader
        narrative sections instead of leaving them unset (the previous
        version of this template never filled these placeholders at all)."""
        home = enriched.get("home_team", "Local")
        away = enriched.get("away_team", "Visitante")

        strategic_context = (
            f"{home}: {enriched.get('home_position')}º con {enriched.get('home_points')} pts "
            f"({enriched.get('home_played')} PJ)\n"
            f"{away}: {enriched.get('away_position')}º con {enriched.get('away_points')} pts "
            f"({enriched.get('away_played')} PJ)"
        )

        deep_tactical_analysis = (
            f"{home} - Fortalezas:\n{enriched.get('home_strengths')}\n"
            f"{home} - Debilidades:\n{enriched.get('home_weaknesses')}\n\n"
            f"{away} - Fortalezas:\n{enriched.get('away_strengths')}\n"
            f"{away} - Debilidades:\n{enriched.get('away_weaknesses')}"
        )

        value_identification = (
            f"Confianza del modelo: {enriched.get('confidence_level')}%. "
            "Este nivel refleja únicamente los datos reales disponibles "
            "(forma, descanso, lesiones, historial directo); no incorpora "
            "métricas avanzadas no disponibles en el plan gratuito."
        )

        return {
            "strategic_context": strategic_context,
            "deep_tactical_analysis": deep_tactical_analysis,
            "physical_analysis": enriched.get("physical_advantage", NOT_AVAILABLE),
            "advanced_metrics_analysis": enriched.get("goal_differential_analysis", NOT_AVAILABLE),
            "detailed_risk_analysis": enriched.get("risk_factors", NOT_AVAILABLE),
            "value_identification": value_identification,
            "full_technical_justification": enriched.get("technical_justification", NOT_AVAILABLE),
            "alternatives_and_combinations": enriched.get("alternative_market_1", NOT_AVAILABLE),
        }

    # ==================== FORM / STRENGTHS ANALYSIS ====================

    def _identify_strengths(self, match_data: Dict, team: str) -> str:
        """Identify team's strengths from real recent form."""
        avg_gf = match_data.get(f"{team}_avg_goals_for")
        avg_ga = match_data.get(f"{team}_avg_goals_against")
        form = match_data.get(f"{team}_form", "")

        strengths = []
        if avg_gf is not None and avg_gf >= 1.8:
            strengths.append(f"• Ataque productivo ({avg_gf} goles/partido de media reciente)")
        if avg_ga is not None and avg_ga <= 0.8:
            strengths.append(f"• Defensa sólida ({avg_ga} goles encajados/partido de media reciente)")
        if form.count("W") >= 3:
            strengths.append(f"• Buena racha de resultados ({form})")

        return "\n".join(strengths) if strengths else "• Sin fortalezas destacadas en los datos disponibles"

    def _identify_weaknesses(self, match_data: Dict, team: str) -> str:
        """Identify team's exploitable weaknesses from real recent form."""
        avg_gf = match_data.get(f"{team}_avg_goals_for")
        avg_ga = match_data.get(f"{team}_avg_goals_against")
        form = match_data.get(f"{team}_form", "")

        weaknesses = []
        if avg_gf is not None and avg_gf <= 0.8:
            weaknesses.append(f"• Ataque poco productivo ({avg_gf} goles/partido de media reciente)")
        if avg_ga is not None and avg_ga >= 1.8:
            weaknesses.append(f"• Defensa vulnerable ({avg_ga} goles encajados/partido de media reciente)")
        if form.count("L") >= 3:
            weaknesses.append(f"• Mala racha de resultados ({form})")

        return "\n".join(weaknesses) if weaknesses else "• Sin debilidades evidentes en los datos disponibles"

    def _goal_differential_analysis(self, match_data: Dict) -> str:
        """Compare real recent goal output between both teams."""
        home_gf = match_data.get("home_avg_goals_for")
        away_gf = match_data.get("away_avg_goals_for")

        if home_gf is None or away_gf is None:
            return NOT_AVAILABLE

        diff = home_gf - away_gf
        if diff > 0.5:
            return f"{match_data.get('home_team', 'Local')} promedia {diff:.2f} goles más por partido en su racha reciente"
        elif diff < -0.5:
            return f"{match_data.get('away_team', 'Visitante')} promedia {abs(diff):.2f} goles más por partido en su racha reciente"
        else:
            return "Producción ofensiva reciente equilibrada entre ambos equipos"

    def _market_odds_summary(self, match_data: Dict) -> str:
        """Real bookmaker odds (The Odds API), when available - never
        fabricated, and never removes the bookmaker's margin (raw implied
        probability, not a "true" probability)."""
        odds = match_data.get("market_odds")
        if not odds:
            return NOT_AVAILABLE

        avg_prices = odds.get("avg_decimal_odds") or {}
        implied = odds.get("implied_probability_pct") or {}
        if not avg_prices:
            return NOT_AVAILABLE

        lines = [
            f"- {name}: cuota media {price} (prob. implícita {implied.get(name, 'N/D')}%)"
            for name, price in avg_prices.items()
        ]
        count = odds.get("bookmakers_count", 0)
        return f"Cuotas reales promediadas de {count} casa(s) de apuestas:\n" + "\n".join(lines)

    def _determine_tactical_advantage(self, match_data: Dict) -> str:
        """Which team looks stronger based on real recent form and goals."""
        home_gf = match_data.get("home_avg_goals_for")
        away_gf = match_data.get("away_avg_goals_for")
        home_form = match_data.get("home_form", "")
        away_form = match_data.get("away_form", "")

        if home_gf is None or away_gf is None:
            return NOT_AVAILABLE

        home_score = home_form.count("W") * 3 + home_form.count("D")
        away_score = away_form.count("W") * 3 + away_form.count("D")

        if abs(home_gf - away_gf) > 0.4 or abs(home_score - away_score) >= 4:
            leader = "LOCAL" if (home_gf - away_gf) + (home_score - away_score) > 0 else "VISITANTE"
            return f"{leader} llega en mejor forma/producción ofensiva reciente"
        return "Equilibrio - sin ventaja clara en forma reciente"

    # ==================== PHYSICAL ANALYSIS ====================

    def _calculate_fatigue_advantage(self, match_data: Dict) -> str:
        """Calculate which team has physical advantage based on real rest days."""
        home_rest = match_data.get("home_rest_days")
        away_rest = match_data.get("away_rest_days")

        if home_rest is None or away_rest is None:
            return NOT_AVAILABLE

        rest_diff = home_rest - away_rest
        if abs(rest_diff) <= 1:
            return "Condiciones físicas similares (descanso equivalente)"
        team = "LOCAL" if rest_diff > 0 else "VISITANTE"
        return f"Ventaja física {team} por {abs(rest_diff)} día(s) más de descanso"

    # ==================== HEAD-TO-HEAD ANALYSIS ====================

    def _win_conditions(self, h2h: Dict, team_name: str, for_home: bool) -> str:
        matches = h2h.get("matches") or []
        if not matches:
            return "Sin historial directo suficiente"

        wins = 0
        for m in matches:
            home_goals, away_goals = m.get("home_goals", 0), m.get("away_goals", 0)
            is_home = m.get("is_home_for_ref_team", False)
            team_won = (home_goals > away_goals) if is_home else (away_goals > home_goals)
            ref_is_this_team = is_home == for_home
            if team_won and ref_is_this_team:
                wins += 1

        if wins == 0:
            return f"Sin victorias en los últimos {len(matches)} enfrentamientos directos"
        return f"Ha ganado {wins} de los últimos {len(matches)} enfrentamientos directos"

    def _recurring_pattern(self, h2h: Dict) -> str:
        btts = h2h.get("btts_pct")
        over25 = h2h.get("over_2_5_pct")
        if btts is None or over25 is None:
            return "Sin historial directo suficiente para identificar patrones"
        return f"BTTS en el {btts}% de los enfrentamientos directos, Over 2.5 en el {over25}%"

    def _recent_form_impact(self, match_data: Dict) -> str:
        home_injuries = len(match_data.get("home_injuries", []) or [])
        away_injuries = len(match_data.get("away_injuries", []) or [])
        if home_injuries == 0 and away_injuries == 0:
            return "Sin bajas relevantes reportadas en ninguno de los dos equipos"
        return f"{match_data.get('home_team', 'Local')}: {home_injuries} baja(s) reportada(s); {match_data.get('away_team', 'Visitante')}: {away_injuries} baja(s) reportada(s)"

    # ==================== INJURY ANALYSIS ====================

    def _analyze_injuries(self, match_data: Dict, team: str) -> str:
        """Analyze injuries for a team."""
        injuries = match_data.get(f"{team}_injuries", [])

        if not injuries:
            return "Sin bajas importantes"

        analysis = []
        for injury in injuries[:3]:
            analysis.append(f"• {injury.get('player', 'Jugador')} ({injury.get('position', '')}) - Impacto: {injury.get('impact', 'Medio')}")

        return "\n".join(analysis)

    def _identify_key_players_out(self, match_data: Dict) -> str:
        """Identify key players unavailable."""
        key_out = []

        for team in ["home", "away"]:
            injuries = match_data.get(f"{team}_injuries", [])
            for injury in injuries:
                if injury.get("is_key_player", False):
                    key_out.append(f"{injury.get('player')} ({team})")

        return ", ".join(key_out) if key_out else "Ningún jugador clave fuera"

    def _assess_injury_impact(self, match_data: Dict) -> str:
        """Assess overall injury impact."""
        home_injuries = len(match_data.get("home_injuries", []))
        away_injuries = len(match_data.get("away_injuries", []))
        total = home_injuries + away_injuries

        if total >= 5:
            return "Alto - Múltiples bajas importantes"
        elif total >= 3:
            return "Medio - Algunas bajas relevantes"
        else:
            return "Bajo - Sin impacto significativo"

    # ==================== PREDICTION METHODS ====================

    def _recommend_market(self, match_data: Dict) -> str:
        """Recommend betting market based on real recent goal output."""
        home_gf = match_data.get("home_avg_goals_for")
        away_gf = match_data.get("away_avg_goals_for")

        if home_gf is None or away_gf is None:
            return "Sin datos suficientes para recomendar mercado"

        diff = home_gf - away_gf
        if diff > 0.5:
            return "Victoria local"
        elif diff < -0.5:
            return "Victoria visitante o empate"
        else:
            return "Ambos equipos marcan (BTTS) o over/under"

    def _alternative_market(self, match_data: Dict) -> str:
        h2h = match_data.get("h2h_structured") or {}
        over25 = h2h.get("over_2_5_pct")
        if over25 is not None and over25 >= 60:
            return "Over 2.5 goles (respaldado por el historial directo)"
        return "Sin alternativa clara con los datos disponibles"

    def _calculate_stake(self, match_data: Dict) -> int:
        """Calculate recommended stake (1-5 units)."""
        confidence = self._calculate_confidence(match_data)

        if confidence >= 80:
            return 5
        elif confidence >= 65:
            return 4
        elif confidence >= 55:
            return 3
        elif confidence >= 45:
            return 2
        else:
            return 1

    def _calculate_confidence(self, match_data: Dict) -> int:
        """Calculate confidence level (0-100) from real, available signals only.
        The fewer real signals we have, the lower the ceiling - we don't
        backfill missing data with a neutral default to inflate confidence."""
        base_confidence = 50
        signals_available = 0

        home_gf = match_data.get("home_avg_goals_for")
        away_gf = match_data.get("away_avg_goals_for")
        if home_gf is not None and away_gf is not None:
            base_confidence += abs(home_gf - away_gf) * 15
            signals_available += 1

        home_rest = match_data.get("home_rest_days")
        away_rest = match_data.get("away_rest_days")
        if home_rest is not None and away_rest is not None:
            base_confidence += abs(home_rest - away_rest) * 3
            signals_available += 1

        injury_impact = len(match_data.get("home_injuries", []) or []) + len(match_data.get("away_injuries", []) or [])
        base_confidence -= injury_impact * 5
        if match_data.get("home_injuries") is not None:
            signals_available += 1

        h2h = match_data.get("h2h_structured") or {}
        if h2h.get("matches"):
            signals_available += 1

        if signals_available == 0:
            return 30

        return min(90, max(30, int(base_confidence)))

    def _generate_technical_justification(self, match_data: Dict) -> str:
        """Generate technical justification for prediction, from real data only."""
        justifications = []

        home_gf = match_data.get("home_avg_goals_for")
        away_gf = match_data.get("away_avg_goals_for")
        if home_gf is not None and away_gf is not None and abs(home_gf - away_gf) > 0.4:
            team = "LOCAL" if home_gf > away_gf else "VISITANTE"
            justifications.append(f"Superioridad ofensiva reciente del equipo {team} ({home_gf} vs {away_gf} goles/partido)")

        home_rest = match_data.get("home_rest_days")
        away_rest = match_data.get("away_rest_days")
        if home_rest is not None and away_rest is not None and abs(home_rest - away_rest) >= 2:
            team = "LOCAL" if home_rest > away_rest else "VISITANTE"
            justifications.append(f"Ventaja física del equipo {team} ({abs(home_rest - away_rest)} días más de descanso)")

        h2h = match_data.get("h2h_structured") or {}
        if h2h.get("over_2_5_pct") is not None and h2h["over_2_5_pct"] >= 60:
            justifications.append(f"Historial directo con tendencia goleadora (Over 2.5 en el {h2h['over_2_5_pct']}% de los enfrentamientos)")

        return "\n".join(justifications) if justifications else "Datos insuficientes para una justificación técnica sólida - proceder con cautela"

    def _identify_risk_factors(self, match_data: Dict) -> str:
        """Identify main risk factors."""
        risks = []

        if len(match_data.get("home_injuries", []) or []) >= 3:
            risks.append("Múltiples bajas en equipo local")
        if len(match_data.get("away_injuries", []) or []) >= 3:
            risks.append("Múltiples bajas en equipo visitante")

        home_rest = match_data.get("home_rest_days")
        away_rest = match_data.get("away_rest_days")
        if home_rest is not None and away_rest is not None and abs(home_rest - away_rest) <= 1:
            risks.append("Condiciones físicas similares - partido parejo")

        h2h = match_data.get("h2h_structured") or {}
        if not h2h.get("matches"):
            risks.append("Sin historial directo reciente entre estos equipos")

        return "\n".join(risks) if risks else "Riesgo bajo - análisis sólido"

    def _identify_decisive_factor(self, match_data: Dict) -> str:
        """Identify the single most decisive factor from real data."""
        home_rest = match_data.get("home_rest_days")
        away_rest = match_data.get("away_rest_days")
        if home_rest is not None and away_rest is not None and abs(home_rest - away_rest) >= 3:
            return "Ventaja física por descanso"

        home_gf = match_data.get("home_avg_goals_for")
        away_gf = match_data.get("away_avg_goals_for")
        if home_gf is not None and away_gf is not None and abs(home_gf - away_gf) > 0.5:
            return "Diferencia en producción ofensiva reciente"

        return "Equilibrio en los datos disponibles - detalles decidirán"

    def _generate_dynamic_factors(self, enriched: Dict, match_data: Dict) -> Dict:
        """Generate the top supporting factors and executive summary from
        whatever real signals are actually available, instead of fixed text."""
        factors = []

        home_gf = match_data.get("home_avg_goals_for")
        away_gf = match_data.get("away_avg_goals_for")
        if home_gf is not None and away_gf is not None and abs(home_gf - away_gf) > 0.4:
            team = enriched.get("home_team") if home_gf > away_gf else enriched.get("away_team")
            factors.append(f"Mejor producción ofensiva reciente de {team}")

        home_rest = match_data.get("home_rest_days")
        away_rest = match_data.get("away_rest_days")
        if home_rest is not None and away_rest is not None and abs(home_rest - away_rest) >= 2:
            team = enriched.get("home_team") if home_rest > away_rest else enriched.get("away_team")
            factors.append(f"Ventaja de descanso para {team}")

        h2h = match_data.get("h2h_structured") or {}
        if h2h.get("matches"):
            factors.append("Historial directo disponible como referencia")

        while len(factors) < 3:
            factors.append("Sin dato adicional disponible")

        enriched["factor_1"], enriched["factor_2"], enriched["factor_3"] = factors[:3]

        if factors[0] == "Sin dato adicional disponible":
            enriched["executive_summary"] = (
                "Datos reales limitados para este partido - el pronóstico se apoya "
                "principalmente en el historial directo y las lesiones reportadas."
            )
        else:
            enriched["executive_summary"] = (
                f"{factors[0]}. " + (f"{factors[1]}." if factors[1] != "Sin dato adicional disponible" else "")
            ).strip()

        enriched["main_risk"] = enriched.get("risk_factors", "Sin riesgos identificados")

        return enriched

    def get_prompt_stats(self) -> Dict[str, int]:
        """Get statistics about prompt templates."""
        return {
            "total_templates": len(self.templates),
            "full_analysis_length": len(self._get_full_analysis_template()),
            "express_length": len(self._get_express_template()),
            "premium_length": len(self._get_premium_template()),
        }
