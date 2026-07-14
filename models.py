"""
Modelo de datos para el sistema de tracking de picks.
Usa SQLAlchemy ORM sobre PostgreSQL.
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class ResultadoPick(PyEnum):
    PENDIENTE = "pendiente"
    GANADO = "ganado"
    PERDIDO = "perdido"
    NULO = "nulo"
    CASH_OUT = "cash_out"


class TipoSala(PyEnum):
    GRATIS = "gratis"
    VIP_CONSERVADORA = "vip_conservadora"
    VIP_AGRESIVA = "vip_agresiva"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    nombre = Column(String, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    es_admin = Column(Boolean, default=False)

    suscripciones = relationship("Suscripcion", back_populates="usuario")


class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_sala = Column(Enum(TipoSala), nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    activa = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="suscripciones")


class Pick(Base):
    """
    Un pick registrado por el tipster. El histórico completo de esta tabla
    es lo que alimenta el comando /stats y el dashboard de transparencia.
    """
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True)
    deporte = Column(String, nullable=False, index=True)
    liga = Column(String, nullable=True, index=True)
    evento = Column(String, nullable=False)  # ej. "Real Madrid vs Barcelona"
    mercado = Column(String, nullable=False)  # ej. "Over 2.5 goles"
    cuota = Column(Float, nullable=False)
    stake = Column(Float, nullable=False)  # unidades apostadas (ej. 1-5)
    casa_apuestas = Column(String, nullable=True)

    razonamiento_ia = Column(Text, nullable=True)  # generado por Claude
    razonamiento_manual = Column(Text, nullable=True)  # notas del tipster

    tipo_sala = Column(Enum(TipoSala), default=TipoSala.GRATIS)

    resultado = Column(Enum(ResultadoPick), default=ResultadoPick.PENDIENTE)
    unidades_ganadas = Column(Float, nullable=True)  # se calcula al resolver

    fecha_evento = Column(DateTime, nullable=False)
    fecha_publicacion = Column(DateTime, default=datetime.utcnow)
    fecha_resolucion = Column(DateTime, nullable=True)

    telegram_message_id = Column(String, nullable=True)  # para editar el post original


class AlertaValor(Base):
    """
    Alertas generadas por el motor de comparación de cuotas (Fase 2).
    Se guardan igualmente para poder demostrar histórico de detecciones.
    """
    __tablename__ = "alertas_valor"

    id = Column(Integer, primary_key=True)
    evento = Column(String, nullable=False)
    mercado = Column(String, nullable=False)
    casa_apuestas = Column(String, nullable=False)
    cuota_detectada = Column(Float, nullable=False)
    cuota_referencia = Column(Float, nullable=False)  # cuota "sharp" usada de benchmark
    porcentaje_valor = Column(Float, nullable=False)
    explicacion_ia = Column(Text, nullable=True)
    fecha_deteccion = Column(DateTime, default=datetime.utcnow)
    publicada = Column(Boolean, default=False)
