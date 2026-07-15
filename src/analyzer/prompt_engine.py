"""
Advanced Prompt Engine for football match analysis.
Generates sophisticated prompts that emphasize tactical variables,
physical metrics, and real game-changing factors.
"""
from typing import Dict, Any, List, Optional
from string import Template
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class PromptEngine:
    """
    Advanced prompt generation system for football analysis.
    Focuses on tactical variables, physical metrics, and contextual factors
    that truly impact match outcomes.
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
**Competición:** $league_name - Jornada $matchday
**Fecha:** $match_date | **Estadio:** $stadium
**Árbitro:** $referee (estilo: $referee_style)

**Momento de la temporada:**
- Jornada $matchday de $total_matchdays
- Posición $home_team: $home_position° ($home_points pts)
- Posición $away_team: $away_position° ($away_points pts)
- Motivación: $motivation_home / $motivation_away (escala 1-10)

---

## ⚽ ANÁLISIS TÁCTICO PROFUNDO

### $home_team - Sistema de Juego
**Formación base:** $home_formation
**Estilo de juego:** $home_play_style
**Pressing:** $home_pressing_intensity (PPDA: $home_ppda)
**Bloque defensivo:** $home_defensive_block
**Transiciones:** $home_transitions

**Puntos fuertes detectables:**
$home_strengths

**Puntos débiles explotables:**
$home_weaknesses

**Clave táctica:** $home_tactical_key

### $away_team - Sistema de Juego
**Formación base:** $away_formation
**Estilo de juego:** $away_play_style
**Pressing:** $away_pressing_intensity (PPDA: $away_ppda)
**Bloque defensivo:** $away_defensive_block
**Transiciones:** $away_transitions

**Puntos fuertes detectables:**
$away_strengths

**Puntos débiles explotables:**
$away_weaknesses

**Clave táctica:** $away_tactical_key

---

## 📊 MÉTRICAS AVANZADAS (QUE IMPORTAN)

### Presión y Dominio
- **PPDA (Pases por acción defensiva):** $home_ppda vs $away_ppda
  - *Menor PPDA = pressing más intenso*
  - *Diferencia >5 indica ventaja clara en recuperación*
  
- **Posesión en campo rival:** $home_territorial_presence% vs $away_territorial_presence%
  - *Indica capacidad de imponer juego*

- **Progresión ofensiva:** $home_progressive_carries vs $away_progressive_carries
  - *Mide capacidad de generar peligro desde atrás*

### Eficiencia y Peligro
- **xG (Expected Goals):** $home_xg vs $away_xg
  - *Últimos 5 partidos: $home_xg_last5 vs $away_xg_last5*
  - *Tendencia: $xg_trend*
  
- **Tiros a puerta/partido:** $home_shots_on_target vs $away_shots_on_target
  - *Calidad de finalización*

- **Conversión de grandes ocasiones:** $home_big_chances_conversion% vs $away_big_chances_conversion%
  - *Crucial para pronósticos de goles*

### Solidez Defensiva
- **xGA (Expected Goals Against):** $home_xga vs $away_xga
  - *Menor xGA = defensa más sólida*
  
- **Tiros recibidos dentro del área:** $home_shots_in_box_against vs $away_shots_in_box_against
  - *Indica vulnerabilidad defensiva*

- **Paradas del portero:** $home_gk_saves vs $away_gk_saves
  - *Efectividad del guardameta*

### Fatiga y Desgaste Físico (CRÍTICO)
- **Distancia promedio recorrida:** $home_avg_distance_km vs $away_avg_distance_km
  - *Indica intensidad física del equipo*
  
- **Sprint count últimos 3 partidos:** $home_sprints_last3 vs $away_sprints_last3
  - *Fatiga acumulada*

- **Rotaciones probables:** $home_rotations vs $away_rotations
  - *Impacto directo en rendimiento*

- **Días de descanso:** $home_rest_days vs $away_rest_days
  - *Ventaja/desventaja física*

### Set Pieces (Decisivos en partidos igualados)
- **Goles de corners:** $home_corners_goals vs $away_corners_goals
- **Goles de faltas:** $home_freekicks_goals vs $away_freekicks_goals
- **Efectividad ofensiva:** $home_set_pieces_efficiency vs $away_set_pieces_efficiency

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
- Sustitutos disponibles: $available_replacements

### Contexto Ambiental
- **Clima:** $weather_conditions
  - Impacto: $weather_impact
- **Estado del césped:** $pitch_condition
- **Presión de la afición:** $crowd_pressure
- **Viaje:** $travel_fatigue

### Momentos Clave del Partido
- **Minutos 60-75:** $critical_period_analysis
  - *Zona donde se deciden muchos partidos por fatiga*
- **Goles tempraneros:** $early_goal_tendency
  - *Equipos que encajan temprano: $early_goal_vulnerability*

---

## 🎯 CONFRONTACIÓN DIRECTA

### Historial Reciente
**Últimos 5 enfrentamientos:**
$head_to_head

**Patrones identificados:**
- $home_team gana cuando: $home_win_conditions
- $away_team gana cuando: $away_win_conditions
- Patrón recurrente: $recurring_pattern

### Estadísticas Cara a Cara
- **Posesión promedio:** $avg_possession_home% vs $avg_possession_away%
- **Tiros totales:** $avg_shots_home vs $avg_shots_away
- **Eficiencia:** $avg_xg_home vs $avg_xg_away

---

## 📋 INSTRUCCIONES DE ANÁLISIS

### 1. ANÁLISIS TÁCTICO (Obligatorio - Profundidad Máxima)
Analiza CÓMO se enfrentan los estilos de juego:

- **¿Quién impondrá su pressing?** 
  - Analiza PPDA y capacidad de recuperación en campo rival
  - Identifica qué equipo puede dominar la zona de creación
  
- **¿Cómo se construirán los ataques?**
  - ¿Por bandas o por centro?
  - ¿Transiciones rápidas o posesión larga?
  - ¿Qué equipo domina la progresión ofensiva?
  
- **¿Dónde se decidirá el partido?**
  - Zona de creación de juego
  - Espacios entre líneas
  - Juego aéreo vs juego por tierra

- **Ventaja táctica clara:** $tactical_advantage

### 2. ANÁLISIS FÍSICO (Obligatorio - Factor Decisivo)
El fútbol moderno se gana en el minuto 80, no en el 1:

- **¿Quién llega más fresco físicamente?**
  - Compara días de descanso
  - Analiza rotaciones y carga de minutos
  - Evalúa sprint count y desgaste acumulado
  
- **¿Afectará la fatiga al resultado?**
  - ¿Algún equipo con partido europeo reciente?
  - ¿Rotaciones probables en mediocampo?
  - Impacto en minutos 60-80

- **Ventaja física:** $physical_advantage

### 3. ANÁLISIS ESTADÍSTICO (Obligatorio - Datos Relevantes)
NO repitas números, INTERPRETA su significado:

- **xG diferencial:** $xg_differential
  - *¿Quién genera más peligro real?*
  
- **Eficiencia ofensiva vs defensiva:**
  - $home_team convierte $home_conversion_rate% de sus xG
  - $away_team convierte $away_conversion_rate% de sus xG
  - *¿Hay sobre/underperformance?*

- **Set pieces como factor:**
  - ¿Algún equipo depende de corners/faltas?
  - ¿Hay ventaja clara en juego aéreo?

### 4. FACTORES PSICOLÓGICOS (Obligatorio)
- **Presión:** $pressure_analysis
- **Motivación extra:** $motivation_factors
- **Historial reciente:** $recent_form_impact

### 5. PRONÓSTICO (Obligatorio - Con Justificación Técnica)

**Mercado recomendado:** $recommended_market

**Stake recomendado:** $stake/5 unidades

**Nivel de confianza:** $confidence_level%

**Justificación técnica (OBLIGATORIA):**
$technical_justification

**Factores clave que soportan el pronóstico:**
1. $factor_1
2. $factor_2
3. $factor_3

**Factores de riesgo:**
$risk_factors

### 6. ALTERNATIVAS (Opcional pero Valioso)
- Mercado secundario: $alternative_market_1
- Combinada sugerida: $suggested_combination (si aplica)
- Por qué NO recomiendo otros mercados: $market_rejections

---

## ⚠️ REGLAS CRÍTICAS

1. **NO hagas predicciones basadas en estadísticas vacías** - Interpreta el contexto
2. **SIEMPRE justifica técnicamente** - Cada pronóstico necesita argumentos sólidos
3. **PRIORIZA variables tácticas y físicas** - Son las que deciden partidos
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

### 🔄 Alternativa a considerar
$alternative

---

**Recuerda:** Estás analizando para apostadores serios que buscan valor a largo plazo, no para espectadores que quieren emoción. Tu análisis debe reflejar profesionalismo, profundidad táctica y rigor estadístico."""

    def _get_express_template(self) -> str:
        """
        Express analysis template for quick tips.
        Still tactical but condensed.
        """
        return """⚡ ANÁLISIS RÁPIDO: $home_team vs $away_team

**Contexto:** $league_name - Jornada $matchday

**Ventaja táctica:** $tactical_advantage
**Ventaja física:** $physical_advantage

**Métricas clave:**
- xG: $home_xg vs $away_xg (diferencial: $xg_differential)
- PPDA: $home_ppda vs $away_ppda
- Fatiga: $fatigue_advantage

**Factor decisivo:** $decisive_factor

**Pronóstico:** $prediction
**Stake:** $stake/5
**Confianza:** $confidence_level%

$brief_justification"""

    def _get_premium_template(self) -> str:
        """
        Premium analysis template for VIP users.
        Maximum depth with advanced metrics.
        """
        return """# 🔍 ANÁLISIS PREMIUM: $home_team vs $away_team

## 📊 Contexto Estratégico
$strategic_context

## 🧠 Análisis Táctico-Profesional
$deep_tactical_analysis

## 💪 Análisis Físico y Fatiga
$physical_analysis

## 📈 Métricas Avanzadas Interpretadas
$advanced_metrics_analysis

## ⚠️ Factores de Riesgo Detallados
$detailed_risk_analysis

## 💡 Value Identification
$value_identification

## 🎯 Pronóstico Principal
**Mercado:** $recommended_market
**Stake:** $stake/5 unidades
**Confianza:** $confidence_level%
**Probabilidad real estimada:** $estimated_probability%
**Probabilidad implícita:** $implied_probability%
**Value:** $value_assessment

## 📋 Justificación Técnica Completa
$full_technical_justification

## 🔄 Alternativas y Combinadas
$alternatives_and_combinations

## 📊 Seguimiento en Vivo
$live_tracking_indicators"""

    def generate_full_analysis_prompt(self, match_data: Dict[str, Any]) -> str:
        """
        Generate complete analysis prompt with all tactical variables.
        
        Args:
            match_data: Complete match data dictionary
            
        Returns:
            Formatted prompt string
        """
        try:
            # Enrich match data with tactical analysis
            enriched_data = self._enrich_with_tactical_analysis(match_data)
            
            # Generate prompt from template
            prompt = self.templates["full_analysis"].safe_substitute(**enriched_data)
            
            logger.info(f"Generated full analysis prompt ({len(prompt)} chars)")
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating full analysis prompt: {e}", exc_info=True)
            raise
    
    def generate_express_prompt(self, match_data: Dict[str, Any]) -> str:
        """
        Generate express analysis prompt for quick tips.
        
        Args:
            match_data: Match data dictionary
            
        Returns:
            Formatted prompt string
        """
        try:
            enriched_data = self._enrich_with_tactical_analysis(match_data)
            prompt = self.templates["express"].safe_substitute(**enriched_data)
            
            logger.info(f"Generated express prompt ({len(prompt)} chars)")
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating express prompt: {e}", exc_info=True)
            raise
    
    def generate_premium_prompt(self, match_data: Dict[str, Any]) -> str:
        """
        Generate premium analysis prompt for VIP users.
        
        Args:
            match_data: Complete match data dictionary
            
        Returns:
            Formatted prompt string
        """
        try:
            enriched_data = self._enrich_with_tactical_analysis(match_data)
            prompt = self.templates["premium"].safe_substitute(**enriched_data)
            
            logger.info(f"Generated premium prompt ({len(prompt)} chars)")
            return prompt
            
        except Exception as e:
            logger.error(f"Error generating premium prompt: {e}", exc_info=True)
            raise
    
    def _enrich_with_tactical_analysis(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich match data with tactical analysis and derived metrics.
        This is where the magic happens - we calculate the variables that matter.
        
        Args:
            match_data: Raw match data
            
        Returns:
            Enriched data with tactical variables
        """
        enriched = match_data.copy()
        
        # Calculate tactical advantages
        enriched.update({
            # Tactical analysis
            "home_formation": match_data.get("home_formation", "4-3-3"),
            "away_formation": match_data.get("away_formation", "4-3-3"),
            "home_play_style": self._determine_play_style(match_data, "home"),
            "away_play_style": self._determine_play_style(match_data, "away"),
            "home_pressing_intensity": self._calculate_pressing_intensity(match_data, "home"),
            "away_pressing_intensity": self._calculate_pressing_intensity(match_data, "away"),
            "home_defensive_block": self._determine_defensive_block(match_data, "home"),
            "away_defensive_block": self._determine_defensive_block(match_data, "away"),
            "home_transitions": self._analyze_transitions(match_data, "home"),
            "away_transitions": self._analyze_transitions(match_data, "away"),
            
            # Strengths and weaknesses
            "home_strengths": self._identify_strengths(match_data, "home"),
            "home_weaknesses": self._identify_weaknesses(match_data, "home"),
            "away_strengths": self._identify_strengths(match_data, "away"),
            "away_weaknesses": self._identify_weaknesses(match_data, "away"),
            "home_tactical_key": self._identify_tactical_key(match_data, "home"),
            "away_tactical_key": self._identify_tactical_key(match_data, "away"),
            
            # Physical metrics (CRITICAL)
            "home_rest_days": match_data.get("home_rest_days", 7),
            "away_rest_days": match_data.get("away_rest_days", 7),
            "home_avg_distance_km": match_data.get("home_avg_distance_km", 105),
            "away_avg_distance_km": match_data.get("away_avg_distance_km", 105),
            "home_sprints_last3": match_data.get("home_sprints_last3", 450),
            "away_sprints_last3": match_data.get("away_sprints_last3", 450),
            "home_rotations": match_data.get("home_rotations", 3),
            "away_rotations": match_data.get("away_rotations", 3),
            "fatigue_advantage": self._calculate_fatigue_advantage(match_data),
            
            # Advanced metrics
            "xg_differential": self._calculate_xg_differential(match_data),
            "home_conversion_rate": match_data.get("home_conversion_rate", 12),
            "away_conversion_rate": match_data.get("away_conversion_rate", 12),
            "home_big_chances_conversion": match_data.get("home_big_chances_conversion", 35),
            "away_big_chances_conversion": match_data.get("away_big_chances_conversion", 35),
            
            # Set pieces
            "home_corners_goals": match_data.get("home_corners_goals", 5),
            "away_corners_goals": match_data.get("away_corners_goals", 5),
            "home_set_pieces_efficiency": match_data.get("home_set_pieces_efficiency", "Alta"),
            "away_set_pieces_efficiency": match_data.get("away_set_pieces_efficiency", "Alta"),
            
            # Tactical advantages
            "tactical_advantage": self._determine_tactical_advantage(match_data),
            "physical_advantage": self._determine_physical_advantage(match_data),
            "xg_trend": self._analyze_xg_trend(match_data),
            
            # Context
            "referee_style": match_data.get("referee_style", "Equilibrado"),
            "weather_conditions": match_data.get("weather", "Despejado"),
            "weather_impact": self._assess_weather_impact(match_data),
            "pitch_condition": match_data.get("pitch_condition", "Bueno"),
            "crowd_pressure": self._assess_crowd_pressure(match_data),
            "travel_fatigue": self._assess_travel_fatigue(match_data),
            
            # Motivation
            "motivation_home": match_data.get("home_motivation", 7),
            "motivation_away": match_data.get("away_motivation", 7),
            "motivation_factors": self._analyze_motivation(match_data),
            
            # Decisive factors
            "decisive_factor": self._identify_decisive_factor(match_data),
            "critical_period_analysis": self._analyze_critical_period(match_data),
            "early_goal_tendency": self._analyze_early_goals(match_data),
            "early_goal_vulnerability": self._identify_early_goal_vulnerability(match_data),
            
            # Injuries
            "home_injuries_analysis": self._analyze_injuries(match_data, "home"),
            "away_injuries_analysis": self._analyze_injuries(match_data, "away"),
            "key_players_out": self._identify_key_players_out(match_data),
            "injury_impact_level": self._assess_injury_impact(match_data),
            "available_replacements": self._assess_replacements(match_data),
            
            # Prediction
            "recommended_market": self._recommend_market(match_data),
            "stake": self._calculate_stake(match_data),
            "confidence_level": self._calculate_confidence(match_data),
            "technical_justification": self._generate_technical_justification(match_data),
            "risk_factors": self._identify_risk_factors(match_data),
            "factor_1": "",
            "factor_2": "",
            "factor_3": "",
            "alternative_market_1": "",
            "suggested_combination": "",
            "market_rejections": "",
            
            # Summary
            "executive_summary": "",
            "main_risk": "",
            "alternative": "",
        })
        
        # Generate dynamic factors
        enriched = self._generate_dynamic_factors(enriched)
        
        return enriched
    
    # ==================== TACTICAL ANALYSIS METHODS ====================
    
    def _determine_play_style(self, match_data: Dict, team: str) -> str:
        """Determine team's play style based on metrics."""
        possession = match_data.get(f"{team}_possession", 50)
        ppda = match_data.get(f"{team}_ppda", 10)
        
        if possession > 55 and ppda < 10:
            return "Posesión y pressing alto (estilo Guardiola)"
        elif possession < 45 and ppda > 12:
            return "Contragolpe y bloque bajo (estilo Simeone)"
        elif ppda < 10:
            return "Pressing intensivo y transiciones rápidas"
        else:
            return "Posesión controlada y construcción paciente"
    
    def _calculate_pressing_intensity(self, match_data: Dict, team: str) -> str:
        """Calculate pressing intensity description."""
        ppda = match_data.get(f"{team}_ppda", 10)
        
        if ppda < 8:
            return "Muy alto (género Klopp)"
        elif ppda < 10:
            return "Alto (pressing organizado)"
        elif ppda < 12:
            return "Medio (pressing selectivo)"
        else:
            return "Bajo (bloque defensivo)"
    
    def _determine_defensive_block(self, match_data: Dict, team: str) -> str:
        """Determine defensive block style."""
        xga = match_data.get(f"{team}_xga", 1.2)
        
        if xga < 1.0:
            return "Bloque muy bajo y compacto"
        elif xga < 1.3:
            return "Bloque medio-bajo"
        else:
            return "Bloque alto (riesgo de espacios)"
    
    def _analyze_transitions(self, match_data: Dict, team: str) -> str:
        """Analyze team's transition play."""
        progressive_carries = match_data.get(f"{team}_progressive_carries", 150)
        
        if progressive_carries > 200:
            return "Transiciones muy rápidas (estilo contraataque)"
        elif progressive_carries > 150:
            return "Transiciones organizadas"
        else:
            return "Transiciones lentas (posesión larga)"
    
    def _identify_strengths(self, match_data: Dict, team: str) -> str:
        """Identify team's key strengths."""
        strengths = []
        
        xg = match_data.get(f"{team}_xg", 1.5)
        xga = match_data.get(f"{team}_xga", 1.2)
        ppda = match_data.get(f"{team}_ppda", 10)
        
        if xg > 1.8:
            strengths.append("• Ataque potente (xG > 1.8)")
        if xga < 1.0:
            strengths.append("• Defensa sólida (xGA < 1.0)")
        if ppda < 9:
            strengths.append("• Pressing intensivo efectivo")
        
        return "\n".join(strengths) if strengths else "• Rendimiento equilibrado"
    
    def _identify_weaknesses(self, match_data: Dict, team: str) -> str:
        """Identify team's exploitable weaknesses."""
        weaknesses = []
        
        xg = match_data.get(f"{team}_xg", 1.5)
        xga = match_data.get(f"{team}_xga", 1.2)
        ppda = match_data.get(f"{team}_ppda", 10)
        
        if xg < 1.2:
            weaknesses.append("• Ataque poco efectivo (xG < 1.2)")
        if xga > 1.5:
            weaknesses.append("• Defensa vulnerable (xGA > 1.5)")
        if ppda > 13:
            weaknesses.append("• Pressing débil (espacios entre líneas)")
        
        return "\n".join(weaknesses) if weaknesses else "• Pocas debilidades evidentes"
    
    def _identify_tactical_key(self, match_data: Dict, team: str) -> str:
        """Identify the tactical key for the team."""
        ppda = match_data.get(f"{team}_ppda", 10)
        xg = match_data.get(f"{team}_xg", 1.5)
        
        if ppda < 9 and xg > 1.5:
            return "Dominio por pressing alto y finalización"
        elif ppda > 12 and xg > 1.5:
            return "Efectividad en contragolpes"
        else:
            return "Control de juego y paciencia ofensiva"
    
    # ==================== PHYSICAL ANALYSIS METHODS ====================
    
    def _calculate_fatigue_advantage(self, match_data: Dict) -> str:
        """Calculate which team has physical advantage."""
        home_rest = match_data.get("home_rest_days", 7)
        away_rest = match_data.get("away_rest_days", 7)
        home_sprints = match_data.get("home_sprints_last3", 450)
        away_sprints = match_data.get("away_sprints_last3", 450)
        
        rest_diff = home_rest - away_rest
        sprint_diff = home_sprints - away_sprints
        
        if rest_diff >= 2 and sprint_diff < -50:
            return "Ventaja física LOCAL (más descanso, menor desgaste)"
        elif rest_diff <= -2 and sprint_diff > 50:
            return "Ventaja física VISITANTE"
        elif abs(rest_diff) <= 1:
            return "Condiciones físicas similares"
        else:
            return f"Ventaja LOCAL por {rest_diff} días extra de descanso"
    
    def _determine_physical_advantage(self, match_data: Dict) -> str:
        """Determine physical advantage in detail."""
        return self._calculate_fatigue_advantage(match_data)
    
    # ==================== METRICS ANALYSIS ====================
    
    def _calculate_xg_differential(self, match_data: Dict) -> str:
        """Calculate xG differential with interpretation."""
        home_xg = match_data.get("home_xg", 1.5)
        away_xg = match_data.get("away_xg", 1.5)
        diff = home_xg - away_xg
        
        if diff > 0.5:
            return f"+{diff:.2f} (ventaja LOCAL clara)"
        elif diff < -0.5:
            return f"{diff:.2f} (ventaja VISITANTE clara)"
        else:
            return f"{diff:+.2f} (equilibrado)"
    
    def _analyze_xg_trend(self, match_data: Dict) -> str:
        """Analyze xG trend for both teams."""
        home_xg_last5 = match_data.get("home_xg_last5", 1.5)
        away_xg_last5 = match_data.get("away_xg_last5", 1.5)
        
        if home_xg_last5 > away_xg_last5 * 1.2:
            return "LOCAL en racha ofensiva"
        elif away_xg_last5 > home_xg_last5 * 1.2:
            return "VISITANTE en racha ofensiva"
        else:
            return "Forma ofensiva similar"
    
    # ==================== CONTEXT ANALYSIS ====================
    
    def _assess_weather_impact(self, match_data: Dict) -> str:
        """Assess weather impact on match."""
        weather = match_data.get("weather", "Despejado")
        
        if "lluvia" in weather.lower():
            return "Alto - Balón rápido, menos control técnico"
        elif "viento" in weather.lower():
            return "Medio - Afecta juego aéreo y pases largos"
        else:
            return "Bajo - Condiciones normales"
    
    def _assess_crowd_pressure(self, match_data: Dict) -> str:
        """Assess crowd pressure impact."""
        home_position = match_data.get("home_position", 10)
        
        if home_position <= 6:
            return "Alto - Afición exigente por resultados"
        elif home_position <= 15:
            return "Medio - Presión moderada"
        else:
            return "Bajo - Sin presión significativa"
    
    def _assess_travel_fatigue(self, match_data: Dict) -> str:
        """Assess travel fatigue for away team."""
        # Simplified - would need real travel distance data
        return "Medio - Viaje estándar"
    
    def _analyze_motivation(self, match_data: Dict) -> str:
        """Analyze motivation factors."""
        home_motivation = match_data.get("home_motivation", 7)
        away_motivation = match_data.get("away_motivation", 7)
        
        factors = []
        if home_motivation >= 9:
            factors.append("LOCAL: Partido crucial")
        if away_motivation >= 9:
            factors.append("VISITANTE: Partido crucial")
        
        return "; ".join(factors) if factors else "Motivación estándar"
    
    def _identify_decisive_factor(self, match_data: Dict) -> str:
        """Identify the single most decisive factor."""
        # Priority: Physical > Tactical > Statistical
        rest_diff = abs(match_data.get("home_rest_days", 7) - match_data.get("away_rest_days", 7))
        
        if rest_diff >= 3:
            return "Ventaja física por descanso"
        
        xg_diff = abs(match_data.get("home_xg", 1.5) - match_data.get("away_xg", 1.5))
        if xg_diff > 0.5:
            return "Superioridad ofensiva (xG)"
        
        ppda_diff = abs(match_data.get("home_ppda", 10) - match_data.get("away_ppda", 10))
        if ppda_diff > 3:
            return "Dominio en pressing"
        
        return "Equilibrio táctico - detalles decidirán"
    
    def _analyze_critical_period(self, match_data: Dict) -> str:
        """Analyze critical period (minutes 60-75)."""
        home_sprints = match_data.get("home_sprints_last3", 450)
        away_sprints = match_data.get("away_sprints_last3", 450)
        
        if home_sprints > away_sprints + 50:
            return "LOCAL mantendrá intensidad - peligro en contraataques rivales"
        elif away_sprints > home_sprints + 50:
            return "VISITANTE con más energía en fase final"
        else:
            return "Ambos equipos con capacidad para definir en fase final"
    
    def _analyze_early_goals(self, match_data: Dict) -> str:
        """Analyze early goal tendency."""
        return "Partido probablemente equilibrado en inicio"
    
    def _identify_early_goal_vulnerability(self, match_data: Dict) -> str:
        """Identify which team concedes early goals."""
        return "Ningún equipo con vulnerabilidad marcada en primeros 15 min"
    
    # ==================== INJURY ANALYSIS ====================
    
    def _analyze_injuries(self, match_data: Dict, team: str) -> str:
        """Analyze injuries for a team."""
        injuries = match_data.get(f"{team}_injuries", [])
        
        if not injuries:
            return "Sin bajas importantes"
        
        analysis = []
        for injury in injuries[:3]:  # Top 3 injuries
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
    
    def _assess_replacements(self, match_data: Dict) -> str:
        """Assess quality of replacements."""
        return "Sustitutos de calidad disponible en ambos equipos"
    
    # ==================== PREDICTION METHODS ====================
    
    def _recommend_market(self, match_data: Dict) -> str:
        """Recommend betting market based on analysis."""
        # This would be more sophisticated in production
        xg_diff = match_data.get("home_xg", 1.5) - match_data.get("away_xg", 1.5)
        
        if xg_diff > 0.5:
            return "Victoria local"
        elif xg_diff < -0.5:
            return "Victoria visitante o empate"
        else:
            return "Ambos equipos marcan (BTTS) o over/under"
    
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
        """Calculate confidence level (0-100)."""
        # Simplified - would use ML model in production
        base_confidence = 50
        
        # Adjust based on xG differential
        xg_diff = abs(match_data.get("home_xg", 1.5) - match_data.get("away_xg", 1.5))
        base_confidence += xg_diff * 20
        
        # Adjust based on injuries
        injury_impact = len(match_data.get("home_injuries", [])) + len(match_data.get("away_injuries", []))
        base_confidence -= injury_impact * 5
        
        # Adjust based on rest days
        rest_diff = abs(match_data.get("home_rest_days", 7) - match_data.get("away_rest_days", 7))
        base_confidence += rest_diff * 3
        
        return min(95, max(30, int(base_confidence)))
    
    def _generate_technical_justification(self, match_data: Dict) -> str:
        """Generate technical justification for prediction."""
        justifications = []
        
        xg_diff = match_data.get("home_xg", 1.5) - match_data.get("away_xg", 1.5)
        if abs(xg_diff) > 0.3:
            team = "LOCAL" if xg_diff > 0 else "VISITANTE"
            justifications.append(f"Superioridad ofensiva clara del equipo {team} (xG differential: {xg_diff:+.2f})")
        
        rest_diff = match_data.get("home_rest_days", 7) - match_data.get("away_rest_days", 7)
        if abs(rest_diff) >= 2:
            team = "LOCAL" if rest_diff > 0 else "VISITANTE"
            justifications.append(f"Ventaja física del equipo {team} ({abs(rest_diff)} días más de descanso)")
        
        ppda_diff = match_data.get("home_ppda", 10) - match_data.get("away_ppda", 10)
        if abs(ppda_diff) > 3:
            team = "LOCAL" if ppda_diff < 0 else "VISITANTE"
            justifications.append(f"Pressing más efectivo del equipo {team} (PPDA diff: {abs(ppda_diff):.1f})")
        
        return "\n".join(justifications) if justifications else "Análisis basado en equilibrio táctico y factores contextuales"
    
    def _identify_risk_factors(self, match_data: Dict) -> str:
        """Identify main risk factors."""
        risks = []
        
        if len(match_data.get("home_injuries", [])) >= 3:
            risks.append("Múltiples bajas en equipo local")
        if len(match_data.get("away_injuries", [])) >= 3:
            risks.append("Múltiples bajas en equipo visitante")
        
        rest_diff = abs(match_data.get("home_rest_days", 7) - match_data.get("away_rest_days", 7))
        if rest_diff <= 1:
            risks.append("Condiciones físicas similares - partido parejo")
        
        return "\n".join(risks) if risks else "Riesgo bajo - análisis sólido"
    
    def _generate_dynamic_factors(self, enriched: Dict) -> Dict:
        """Generate dynamic factors for the analysis."""
        # Factor 1, 2, 3
        enriched["factor_1"] = "Superioridad táctica en pressing"
        enriched["factor_2"] = "Ventaja física por descanso"
        enriched["factor_3"] = "Eficiencia en finalización"
        
        # Alternatives
        enriched["alternative_market_1"] = "Over 2.5 goles"
        enriched["suggested_combination"] = "Victoria local + Over 1.5 goles"
        enriched["market_rejections"] = "Empate - xG no respalda igualdad"
        
        # Summary
        enriched["executive_summary"] = "Ventaja táctica y física clara del equipo local. Pressing alto y mayor descanso generan superioridad esperada."
        enriched["main_risk"] = "Fatiga acumulada podría reducir intensidad en minutos finales"
        enriched["alternative"] = "Considerar Over 2.5 goles como alternativa más segura"
        
        return enriched
    
    def get_prompt_stats(self) -> Dict[str, int]:
        """Get statistics about prompt templates."""
        return {
            "total_templates": len(self.templates),
            "full_analysis_length": len(self._get_full_analysis_template()),
            "express_length": len(self._get_express_template()),
            "premium_length": len(self._get_premium_template()),
        }