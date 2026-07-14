"""
Bot de Telegram — punto de entrada.
Comandos disponibles (fase 1):
  /nuevopick   -> registrar un pick (solo admin)
  /resolver    -> marcar un pick como ganado/perdido/nulo (solo admin)
  /stats       -> ver estadísticas reales (cualquier usuario)
  /ultimos     -> ver los últimos picks publicados
"""
import asyncio
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from db.database import init_db, SessionLocal
from db.models import Pick, ResultadoPick, Usuario
from backend.stats import calcular_stats, resolver_pick
from backend.ai_engine import generar_razonamiento

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = set(os.getenv("ADMIN_TELEGRAM_IDS", "").split(","))  # IDs separados por coma

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


def es_admin(message: Message) -> bool:
    return str(message.from_user.id) in ADMIN_IDS


# ---------- FSM para el flujo de registrar un pick ----------
class NuevoPickForm(StatesGroup):
    deporte = State()
    evento = State()
    mercado = State()
    cuota = State()
    stake = State()
    notas = State()


@dp.message(Command("nuevopick"))
async def cmd_nuevopick(message: Message, state: FSMContext):
    if not es_admin(message):
        await message.answer("Este comando es solo para el equipo de análisis.")
        return
    await state.set_state(NuevoPickForm.deporte)
    await message.answer("Vamos a registrar un pick.\n\n¿Deporte? (ej. Fútbol, Baloncesto)")


@dp.message(NuevoPickForm.deporte)
async def paso_deporte(message: Message, state: FSMContext):
    await state.update_data(deporte=message.text)
    await state.set_state(NuevoPickForm.evento)
    await message.answer("¿Evento? (ej. Real Madrid vs Barcelona)")


@dp.message(NuevoPickForm.evento)
async def paso_evento(message: Message, state: FSMContext):
    await state.update_data(evento=message.text)
    await state.set_state(NuevoPickForm.mercado)
    await message.answer("¿Mercado? (ej. Over 2.5 goles)")


@dp.message(NuevoPickForm.mercado)
async def paso_mercado(message: Message, state: FSMContext):
    await state.update_data(mercado=message.text)
    await state.set_state(NuevoPickForm.cuota)
    await message.answer("¿Cuota? (ej. 1.85)")


@dp.message(NuevoPickForm.cuota)
async def paso_cuota(message: Message, state: FSMContext):
    try:
        cuota = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Formato no válido. Escribe la cuota como número, ej. 1.85")
        return
    await state.update_data(cuota=cuota)
    await state.set_state(NuevoPickForm.stake)
    await message.answer("¿Stake? (unidades, ej. 2)")


@dp.message(NuevoPickForm.stake)
async def paso_stake(message: Message, state: FSMContext):
    try:
        stake = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Formato no válido. Escribe el stake como número, ej. 2")
        return
    await state.update_data(stake=stake)
    await state.set_state(NuevoPickForm.notas)
    await message.answer("Notas del análisis (breve, la IA las redactará mejor):")


@dp.message(NuevoPickForm.notas)
async def paso_notas(message: Message, state: FSMContext):
    data = await state.update_data(notas=message.text)
    await message.answer("Generando razonamiento con IA...")

    try:
        razonamiento = generar_razonamiento(
            evento=data["evento"],
            mercado=data["mercado"],
            cuota=data["cuota"],
            notas_tipster=data["notas"],
        )
    except Exception as e:
        logger.error(f"Error generando razonamiento IA: {e}")
        razonamiento = data["notas"]  # fallback: usar las notas tal cual

    db = SessionLocal()
    try:
        from datetime import datetime
        pick = Pick(
            deporte=data["deporte"],
            evento=data["evento"],
            mercado=data["mercado"],
            cuota=data["cuota"],
            stake=data["stake"],
            razonamiento_ia=razonamiento,
            razonamiento_manual=data["notas"],
            fecha_evento=datetime.utcnow(),  # ajustar con fecha real del evento
        )
        db.add(pick)
        db.commit()
        db.refresh(pick)

        texto_publicacion = (
            f"🎯 <b>NUEVO PICK #{pick.id}</b>\n\n"
            f"🏆 {pick.deporte} — {pick.evento}\n"
            f"📊 {pick.mercado}\n"
            f"💰 Cuota: {pick.cuota}  |  Stake: {pick.stake}u\n\n"
            f"🧠 {razonamiento}\n\n"
            f"<i>Histórico verificable con /stats</i>"
        )
        await message.answer(texto_publicacion, parse_mode="HTML")
    finally:
        db.close()

    await state.clear()


# ---------- Resolver un pick ----------
@dp.message(Command("resolver"))
async def cmd_resolver(message: Message):
    if not es_admin(message):
        await message.answer("Este comando es solo para el equipo de análisis.")
        return

    partes = message.text.split()
    if len(partes) != 3:
        await message.answer(
            "Uso: /resolver <id_pick> <resultado>\n"
            "Resultado: ganado | perdido | nulo\n"
            "Ejemplo: /resolver 5 ganado"
        )
        return

    try:
        pick_id = int(partes[1])
        resultado_str = partes[2].lower()
        resultado_map = {
            "ganado": ResultadoPick.GANADO,
            "perdido": ResultadoPick.PERDIDO,
            "nulo": ResultadoPick.NULO,
        }
        resultado = resultado_map.get(resultado_str)
        if not resultado:
            raise ValueError
    except ValueError:
        await message.answer("Resultado no válido. Usa: ganado, perdido o nulo.")
        return

    db = SessionLocal()
    try:
        pick = resolver_pick(db, pick_id, resultado)
        if not pick:
            await message.answer(f"No se encontró el pick #{pick_id}")
            return
        emoji = "✅" if resultado == ResultadoPick.GANADO else "❌" if resultado == ResultadoPick.PERDIDO else "➖"
        await message.answer(
            f"{emoji} Pick #{pick.id} resuelto: {resultado_str}\n"
            f"Unidades: {pick.unidades_ganadas:+.2f}"
        )
    finally:
        db.close()


# ---------- Estadísticas públicas ----------
@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    partes = message.text.split()
    deporte = partes[1] if len(partes) > 1 else None

    db = SessionLocal()
    try:
        stats = calcular_stats(db, deporte=deporte)
    finally:
        db.close()

    if stats["total_picks"] == 0:
        await message.answer("Todavía no hay picks resueltos en el histórico.")
        return

    filtro_txt = f" ({deporte})" if deporte else " (todos los deportes)"
    texto = (
        f"📊 <b>ESTADÍSTICAS REALES{filtro_txt}</b>\n\n"
        f"Picks totales: {stats['total_picks']}\n"
        f"✅ Aciertos: {stats['aciertos']}\n"
        f"❌ Fallos: {stats['fallos']}\n"
        f"🎯 % acierto: {stats['porcentaje_acierto']}%\n"
        f"💰 Unidades apostadas: {stats['unidades_apostadas']}\n"
        f"📈 Unidades netas: {stats['unidades_ganadas']:+.2f}\n"
        f"📉 ROI: {stats['roi']:+.1f}%\n\n"
        f"<i>Histórico calculado en tiempo real, sin datos ocultos.</i>"
    )
    await message.answer(texto, parse_mode="HTML")


# ---------- Últimos picks ----------
@dp.message(Command("ultimos"))
async def cmd_ultimos(message: Message):
    db = SessionLocal()
    try:
        picks = db.query(Pick).order_by(Pick.fecha_publicacion.desc()).limit(5).all()
    finally:
        db.close()

    if not picks:
        await message.answer("Todavía no hay picks publicados.")
        return

    emoji_map = {
        ResultadoPick.GANADO: "✅",
        ResultadoPick.PERDIDO: "❌",
        ResultadoPick.NULO: "➖",
        ResultadoPick.PENDIENTE: "⏳",
        ResultadoPick.CASH_OUT: "💸",
    }

    lineas = ["📋 <b>ÚLTIMOS 5 PICKS</b>\n"]
    for p in picks:
        emoji = emoji_map.get(p.resultado, "⏳")
        lineas.append(f"{emoji} #{p.id} — {p.evento} ({p.mercado}) @ {p.cuota}")

    await message.answer("\n".join(lineas), parse_mode="HTML")


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Bienvenido al canal.\n\n"
        "Comandos disponibles:\n"
        "/stats — ver estadísticas reales del canal\n"
        "/ultimos — ver los últimos picks publicados"
    )


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("Falta la variable de entorno TELEGRAM_BOT_TOKEN")
    init_db()
    logger.info("Base de datos inicializada. Arrancando bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
