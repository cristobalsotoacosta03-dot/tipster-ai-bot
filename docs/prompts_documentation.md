# 📝 Documentación de Prompts - Sistema de Análisis

Este documento describe la arquitectura de prompts utilizada por el sistema de análisis de Tipster IA.

## 🎯 Filosofía del Prompt Engineering

Nuestro sistema de prompts está diseñado para maximizar la calidad del análisis de apuestas deportivas mediante:

1. **Contextualización profunda:** Proporcionar a Claude toda la información relevante del partido
2. **Instrucciones específicas:** Definir exactamente qué tipo de análisis necesitamos
3. **Formato estructurado:** Garantizar respuestas consistentes y útiles
4. **Optimización de tokens:** Minimizar costes manteniendo calidad

## 🧠 Prompt Maestro de Análisis

### System Prompt (Contexto Base)

```
Eres un experto analista de apuestas deportivas con más de 15 años de experiencia 
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

Recuerda: El objetivo es el valor a largo plazo, no ganar siempre.
```

### User Prompt Template (Estructura del Análisis)

```markdown
# ANÁLISIS DE PARTIDO

## 📊 DATOS DEL PARTIDO
- **Liga:** {league_name}
- **Jornada:** {matchday}
- **Fecha:** {match_date}
- **Estadio:** {stadium}
- **Árbitro:** {referee}

## ⚽ EQUIPOS

### {home_team}
- **Posición en liga:** {home_position}
- **Puntos:** {home_points}
- **Racha reciente:** {home_form}
- **Goles a favor/en contra:** {home_goals_for}/{home_goals_against}
- **xG promedio:** {home_xg}
- **Lesiones clave:** {home_injuries}
- **Sancionados:** {home_suspensions}

### {away_team}
- **Posición en liga:** {away_position}
- **Puntos:** {away_points}
- **Racha reciente:** {away_form}
- **Goles a favor/en contra:** {away_goals_for}/{away_goals_against}
- **xG promedio:** {away_xg}
- **Lesiones clave:** {away_injuries}
- **Sancionados:** {away_suspensions}

## 📈 ESTADÍSTICAS COMPARATIVAS
- **Posesión promedio:** {home_possession}% vs {away_possession}%
- **PPDA (pressing):** {home_ppda} vs {away_ppda}
- **xG últimos 5 partidos:** {home_xg_last5} vs {away_xg_last5}
- **Eficiencia defensiva:** {home_defensive_rating} vs {away_defensive_rating}
- **Tiros a puerta/partido:** {home_shots_on_target} vs {away_shots_on_target}

## 🏆 CONTEXTO HISTÓRICO
- **Últimos 5 enfrentamientos:** {head_to_head}
- **Victoria última local:** {last_home_win}
- **Victoria última visitante:** {last_away_win}

## 🎯 FACTORES ADICIONALES
- **Motivación:** {motivation}
- **Calendario:** {schedule_context}
- **Clima/estado del campo:** {weather}
- **Apuestas del público:** {public_betting}

---

## 📋 INSTRUCCIONES DE ANÁLISIS

Realiza un análisis TÁCTICO y ESTADÍSTICO profundo. NO hagas predicciones aleatorias.

### 1. ANÁLISIS TÁCTICO (Obligatorio)
- Sistemas de juego probables (4-3-3, 4-2-3-1, etc.)
- Estrategia de pressing y bloque defensivo
- Puntos fuertes y débiles detectables
- Claves tácticas del partido

### 2. ANÁLISIS ESTADÍSTICO (Obligatorio)
- Comparativa detallada de métricas avanzadas
- Tendencias identificables en datos recientes
- Rendimiento en situaciones específicas (local/visitante)
- Correlaciones estadísticas relevantes

### 3. FACTORES DE RIESGO (Obligatorio)
- Lesiones/sanciones que afecten el rendimiento
- Factores motivacionales (descenso, título, europeo)
- Presión externa (afición, prensa)
- Factores ambientales adversos

### 4. PRONÓSTICO (Obligatorio)
- **Mercado recomendado:** {recommended_market}
- **Stake recomendado:** {stake}/5 unidades
- **Confianza:** {confidence_level}%
- **Justificación técnica detallada**

### 5. ALTERNATIVAS (Opcional)
- Mercados secundarios con valor
- Combinadas recomendadas (si aplica)
- Explicación de por qué NO otros mercados

---

## ⚠️ FORMATO DE RESPUESTA

Estructura tu respuesta EXACTAMENTE así:

### 🎯 ANÁLISIS TÁCTICO
[Tu análisis aquí]

### 📊 DATOS CLAVE
[Estadísticas relevantes]

### ⚠️ RIESGOS
[Factores de riesgo]

### 💰 PRONÓSTICO
**Mercado:** [mercado]
**Stake:** [X]/5 unidades
**Confianza:** [X]%
**Justificación:** [explicación técnica]

### 🔄 ALTERNATIVAS
[Opciones secundarias si existen]

---

Recuerda: Si no hay valor claro, dilo. Mejor no analizar que dar un pronóstico sin fundamento.
```

## 🔧 Variables Dinámicas

### Datos del Partido
- `{league_name}` - Nombre de la liga/competición
- `{matchday}` - Número de jornada
- `{match_date}` - Fecha y hora del partido
- `{stadium}` - Estadio donde se juega
- `{referee}` - Árbitro principal

### Estadísticas de Equipos
- `{home_position}` / `{away_position}` - Posición en la tabla
- `{home_points}` / `{away_points}` - Puntos acumulados
- `{home_form}` / `{away_form}` - Racha reciente (últimos 5 resultados)
- `{home_goals_for}` / `{away_goals_for}` - Goles marcados
- `{home_goals_against}` / `{away_goals_against}` - Goles recibidos
- `{home_xg}` / `{away_xg}` - Expected Goals promedio
- `{home_injuries}` / `{away_injuries}` - Lista de lesionados
- `{home_suspensions}` / `{away_suspensions}` - Jugadores sancionados

### Métricas Avanzadas
- `{home_possession}` / `{away_possession}` - Posesión promedio %
- `{home_ppda}` / `{away_ppda}` - PPDA (pressing intensity)
- `{home_xg_last5}` / `{away_xg_last5}` - xG últimos 5 partidos
- `{home_defensive_rating}` / `{away_defensive_rating}` - Rating defensivo
- `{home_shots_on_target}` / `{away_shots_on_target}` - Tiros a puerta/partido

### Contexto
- `{head_to_head}` - Últimos enfrentamientos directos
- `{motivation}` - Nivel de motivación (1-10)
- `{schedule_context}` - Contexto de calendario
- `{weather}` - Condiciones climáticas
- `{public_betting}` - Distribución de apuestas del público

## 🎨 Variantes de Prompt

### Análisis Express (Para Tips Rápidos)
Versión reducida para análisis rápidos en el canal gratuito:

```markdown
Análisis rápido de {home_team} vs {away_team}:

**Contexto:** {league_name} - Jornada {matchday}

**Estadísticas clave:**
- Posición: {home_position}° vs {away_position}°
- xG: {home_xg} vs {away_xg}
- Forma: {home_form} vs {away_form}

**Pronóstico:** {prediction}
**Stake:** {stake}/5
**Confianza:** {confidence}%
```

### Análisis Premium (Para VIP)
Versión extendida con profundidad máxima:

```markdown
# ANÁLISIS PREMIUM: {home_team} vs {away_team}

## 📊 Contexto del Partido
[Análisis detallado de situación en liga, motivaciones, calendario]

## 🧠 Análisis Táctico Profundo
[Análisis de sistemas de juego, pressing, transiciones,构建ción]

## 📈 Métricas Avanzadas
[Análisis detallado de xG, PPDA, eficiencia, tendencias]

## ⚠️ Factores de Riesgo
[Análisis exhaustivo de lesiones, sanciones, presión, ambiente]

## 💡 Value Identification
[Identificación de value bets con cálculo de probabilidad implícita]

## 🎯 Pronóstico Principal
**Mercado:** [mercado]
**Stake:** [X]/5
**Confianza:** [X]%
**Probabilidad real estimada:** [X]%
**Probabilidad implícita:** [X]%
**Value:** [Sí/No] - [Explicación]

## 🔄 Alternativas y Combinadas
[Análisis de mercados secundarios y posibles combinadas]

## 📋 Seguimiento
[Indicadores a monitorear durante el partido]
```

## 🔍 Optimización de Tokens

### Estrategias Implementadas

1. **Cache Agresivo:**
   - Análisis cacheados por 6 horas
   - No regenerar análisis del mismo partido
   - Ahorro estimado: 60-80% en costes de API

2. **Prompt Condensado:**
   - Solo incluir estadísticas relevantes
   - Eliminar redundancias
   - Usar formato compacto

3. **Context Window Management:**
   - Limitar historial de conversación
   - Resumir análisis previos
   - Enfocarse en datos actuales

4. **Temperature Optimization:**
   - `temperature=0.7` para balance creatividad/consistencia
   - Ajustar según tipo de análisis

## 📊 Métricas de Calidad

### KPIs del Prompt
- **Tasa de acierto:** > 55% a largo plazo
- **ROI por unidad:** > 1.10
- **Valor identificado:** > 70% de análisis con value claro
- **Tiempo de generación:** < 30 segundos por análisis
- **Coste por análisis:** < €0.50

### Evaluación Continua
- Revisar weekly: precisión de pronósticos
- Ajustar prompts según rendimiento
- A/B testing de variantes
- Feedback loop con resultados reales

## 🚀 Mejoras Futuras

### Día 7+
- [ ] Fine-tuning de prompts basado en resultados
- [ ] Sistema de aprendizaje automático
- [ ] Análisis de sentimiento en redes sociales
- [ ] Integración de datos de lesiones en tiempo real
- [ ] Análisis de alineaciones confirmadas
- [ ] Sistema de alertas automáticas

## 📝 Notas de Implementación

### Para Desarrolladores

1. **Modificación de Prompts:**
   - Editar en `src/analyzer/prompt_engine.py`
   - Probar cambios en ambiente de desarrollo primero
   - Documentar variantes en este archivo

2. **Testing:**
   - Usar casos de prueba reales
   - Validar formato de salida
   - Verificar consistencia

3. **Monitoreo:**
   - Loggear todos los prompts enviados
   - Analizar costes por análisis
   - Medir tiempo de respuesta

## 🔗 Referencias

- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Claude 3.5 Sonnet Documentation](https://docs.anthropic.com/claude/docs/claude-3-5-sonnet)
- [Football Analytics Best Practices](https://statsbomb.com/articles/)

---

**Última actualización:** Día 1 del Sprint - 15/07/2026
**Versión:** 1.0.0