"""
Cálculo de estadísticas reales a partir del histórico de picks.
Esto es lo que alimenta /stats y el futuro dashboard — la pieza clave
de "transparencia verificable" del proyecto.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from db.models import Pick, ResultadoPick


def calcular_stats(db: Session, deporte: str = None, dias: int = None):
    """
    Calcula % de acierto, ROI y unidades netas.
    - deporte: filtra por deporte concreto (None = todos)
    - dias: filtra por ventana de tiempo (None = histórico completo)
    """
    query = db.query(Pick).filter(Pick.resultado != ResultadoPick.PENDIENTE)

    if deporte:
        query = query.filter(Pick.deporte == deporte)

    if dias:
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        query = query.filter(Pick.fecha_evento >= fecha_limite)

    picks = query.all()

    if not picks:
        return {
            "total_picks": 0,
            "aciertos": 0,
            "fallos": 0,
            "porcentaje_acierto": 0.0,
            "unidades_apostadas": 0.0,
            "unidades_ganadas": 0.0,
            "roi": 0.0,
        }

    total = len(picks)
    aciertos = sum(1 for p in picks if p.resultado == ResultadoPick.GANADO)
    fallos = sum(1 for p in picks if p.resultado == ResultadoPick.PERDIDO)

    unidades_apostadas = sum(p.stake for p in picks)
    unidades_ganadas = sum(p.unidades_ganadas or 0.0 for p in picks)

    roi = (unidades_ganadas / unidades_apostadas * 100) if unidades_apostadas > 0 else 0.0
    porcentaje_acierto = (aciertos / total * 100) if total > 0 else 0.0

    return {
        "total_picks": total,
        "aciertos": aciertos,
        "fallos": fallos,
        "porcentaje_acierto": round(porcentaje_acierto, 1),
        "unidades_apostadas": round(unidades_apostadas, 2),
        "unidades_ganadas": round(unidades_ganadas, 2),
        "roi": round(roi, 1),
    }


def resolver_pick(db: Session, pick_id: int, resultado: ResultadoPick):
    """
    Marca un pick como ganado/perdido/nulo y calcula las unidades ganadas.
    Regla estándar: ganado = stake * (cuota - 1); perdido = -stake; nulo = 0.
    """
    pick = db.query(Pick).filter(Pick.id == pick_id).first()
    if not pick:
        return None

    pick.resultado = resultado
    pick.fecha_resolucion = datetime.utcnow()

    if resultado == ResultadoPick.GANADO:
        pick.unidades_ganadas = round(pick.stake * (pick.cuota - 1), 2)
    elif resultado == ResultadoPick.PERDIDO:
        pick.unidades_ganadas = -pick.stake
    else:  # NULO o CASH_OUT parcial se trata como 0 por defecto
        pick.unidades_ganadas = 0.0

    db.commit()
    db.refresh(pick)
    return pick
