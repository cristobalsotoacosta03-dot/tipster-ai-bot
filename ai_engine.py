"""
Capa de IA (Claude) para generar contenido a partir de un pick.
IMPORTANTE: esta capa NO predice resultados ni cuotas. Su función es
redactar/explicar el análisis que el tipster (humano) ya ha decidido,
y generar contenido derivado. Ver docs/PRINCIPIOS_IA.md.
"""
import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"


def generar_razonamiento(evento: str, mercado: str, cuota: float, notas_tipster: str) -> str:
    """
    Genera un razonamiento corto y profesional a partir de las notas
    que el tipster ya ha escrito. La IA NO decide el pick, solo lo redacta
    y estructura para que sea más claro y presentable.
    """
    prompt = f"""Eres un redactor especializado en análisis deportivo para un canal de Telegram.

Datos del pick (ya decidido por el analista humano):
- Evento: {evento}
- Mercado: {mercado}
- Cuota: {cuota}
- Notas del analista: {notas_tipster}

Redacta un razonamiento breve (máximo 3-4 frases), claro y profesional, que explique
la lógica detrás de este pick basándote SOLO en las notas proporcionadas. No inventes
datos, lesiones o estadísticas que no estén en las notas. No prometas ni sugieras que
el resultado es seguro. Tono directo, sin emojis excesivos, en español."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def generar_resumen_semanal(stats: dict, deporte: str = "general") -> str:
    """Genera un resumen semanal de resultados para publicar como contenido."""
    prompt = f"""Genera un resumen semanal breve (5-6 frases) para publicar en un canal
de Telegram de análisis deportivo, en tono cercano pero profesional, en español.

Datos reales de la semana ({deporte}):
- Picks totales: {stats['total_picks']}
- Aciertos: {stats['aciertos']}
- Fallos: {stats['fallos']}
- % acierto: {stats['porcentaje_acierto']}%
- ROI: {stats['roi']}%

Sé honesto con los números, incluye tanto lo bueno como lo malo si el ROI es negativo.
No prometas rentabilidad futura. No uses frases tipo "apuesta segura" o "no falla"."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def generar_post_redes(evento: str, mercado: str, razonamiento: str, plataforma: str = "x") -> str:
    """Adapta un pick ya publicado a formato de red social (X/Twitter, guión de Reel, etc.)."""
    formato = {
        "x": "un tuit de máximo 280 caracteres, directo, con 1-2 hashtags relevantes",
        "reel": "un guión corto de 15-20 segundos para un Reel/Short, con ganchos de inicio y cierre",
    }.get(plataforma, "un post corto de redes sociales")

    prompt = f"""Convierte este análisis en {formato}, en español.

Evento: {evento}
Mercado: {mercado}
Razonamiento: {razonamiento}

No prometas resultados seguros. Incluye llamada a la acción sutil hacia el canal de Telegram."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
