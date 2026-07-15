"""
Main Telegram Bot implementation.
Handles bot initialization, command routing, and message processing.
"""
import asyncio
from typing import Optional, Dict, Any
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import logging

from config.settings import settings
from src.utils.logger import logger

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram Bot wrapper for the Tipster IA service.
    Handles all bot operations including commands, callbacks, and messages.
    """
    
    def __init__(self):
        """Initialize Telegram bot with token from settings."""
        self.token = settings.telegram_bot_token
        self.admin_id = settings.telegram_admin_id
        self.vip_group_id = settings.telegram_vip_group_id
        
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Telegram bot initialized")
    
    def _register_handlers(self) -> None:
        """Register all command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("analisis", self.analisis_command))
        self.application.add_handler(CommandHandler("premium", self.premium_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Callback query handler (for inline buttons)
        self.application.add_handler(CallbackQueryHandler(self.callback_handler))
        
        # Message handler (for non-command messages)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
        logger.info("All handlers registered")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /start command.
        Welcome message and introduction to the service.
        """
        try:
            user = update.effective_user
            user_id = user.id
            
            logger.info(f"Start command from user {user_id} (@{user.username})")
            
            welcome_message = f"""
👋 ¡Hola {user.first_name}! Bienvenido a **Tipster IA**

🤖 Tu asistente inteligente de análisis de apuestas deportivas impulsado por Claude AI.

**¿Qué puedo hacer por ti?**

📊 **Análisis de partidos** - Análisis táctico y estadístico profundo
💰 **Tips diarios** - Pronósticos con valor estadístico
🎯 **Sistema VIP** - Acceso a análisis premium y grupo exclusivo

**Comandos disponibles:**
/start - Muestra este mensaje
/help - Ver todos los comandos
/analisis - Solicitar análisis de un partido
/premium - Información sobre el plan VIP
/status - Ver estado del servicio

💡 *Usa /analisis seguido de los equipos para obtener tu primer análisis*
            """.strip()
            
            await update.message.reply_text(
                welcome_message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in start_command: {e}", exc_info=True)
            await update.message.reply_text("❌ Error al procesar el comando. Por favor, inténtalo de nuevo.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /help command.
        Show all available commands and their descriptions.
        """
        try:
            help_message = """
📚 **Guía de Comandos - Tipster IA**

**Comandos Básicos:**
/start - Inicia el bot y muestra el mensaje de bienvenida
/help - Muestra esta guía de comandos
/status - Verifica el estado del servicio

**Análisis de Partidos:**
/analisis [equipo1] vs [equipo2] - Análisis completo del partido
Ejemplo: `/analisis Real Madrid vs Barcelona`

**Información Premium:**
/premium - Ver planes y precios del servicio VIP

**Consejos:**
- Los análisis gratuitos están limitados a 2 por día
- El análisis VIP incluye pronósticos detallados con stake recomendado
- Los miembros VIP tienen acceso a un grupo exclusivo con análisis en vivo

💬 Para soporte, contacta con @TuSoporte
            """.strip()
            
            await update.message.reply_text(
                help_message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in help_command: {e}", exc_info=True)
            await update.message.reply_text("❌ Error al mostrar la ayuda. Por favor, inténtalo de nuevo.")
    
    async def analisis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /analisis command.
        Request match analysis (placeholder for Día 2 implementation).
        """
        try:
            user_id = update.effective_user.id
            
            # Check if user provided match info
            if not context.args or len(context.args) < 3:
                await update.message.reply_text(
                    "⚠️ **Uso incorrecto**\n\n"
                    "Formato: `/analisis [equipo1] vs [equipo2]`\n"
                    "Ejemplo: `/analisis Real Madrid vs Barcelona`\n\n"
                    "💡 *Esta funcionalidad estará disponible mañana (Día 2 del sprint)*",
                    parse_mode="Markdown"
                )
                return
            
            match_query = " ".join(context.args)
            logger.info(f"Analysis request from user {user_id}: {match_query}")
            
            # TODO: Implement actual analysis on Día 2
            await update.message.reply_text(
                f"🔍 **Análisis solicitado:** {match_query}\n\n"
                "⏳ Esta funcionalidad estará disponible mañana.\n"
                "Estamos ultimando el motor de análisis con IA.\n\n"
                "🎁 Mientras tanto, disfruta de nuestros tips diarios en el canal gratuito.",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in analisis_command: {e}", exc_info=True)
            await update.message.reply_text("❌ Error al procesar el análisis. Por favor, inténtalo de nuevo.")
    
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /premium command.
        Show VIP subscription information.
        """
        try:
            premium_message = """
⭐ **Plan VIP - Tipster IA**

**¿Qué incluye?**
✅ Análisis diarios de 3-5 partidos seleccionados
✅ Pronósticos con stake recomendado (1-5 unidades)
✅ Análisis táctico avanzado y estadísticas métricas
✅ Acceso al grupo VIP de Telegram exclusivo
✅ Seguimiento en vivo de picks durante los partidos
✅ Historial de resultados y estadísticas de acierto
✅ Soporte prioritario

**Precios:**
📅 **Mensual:** €29.99/mes
📆 **Anual:** €299/año (ahorra 2 meses)

**Garantía:**
🔒 Garantía de satisfacción de 7 días. Si no estás satisfecho, te devolvemos tu dinero.

**Para suscribirte:**
Contacta con @TuSoporte o usa el botón de pago (próximamente).

🎯 *El value betting es a largo plazo. Confía en el proceso.*
            """.strip()
            
            await update.message.reply_text(
                premium_message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in premium_command: {e}", exc_info=True)
            await update.message.reply_text("❌ Error al mostrar la información premium. Por favor, inténtalo de nuevo.")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /status command.
        Show bot status and statistics.
        """
        try:
            # TODO: Add real statistics on Día 3
            status_message = """
✅ **Estado del Servicio - Tipster IA**

**Sistema:** Operativo
🤖 **Bot:** En línea
🧠 **Claude AI:** Conectado
📊 **API de Datos:** Configurada

**Estadísticas:**
👥 Usuarios activos: Próximamente
📈 Análisis generados: Próximamente
🎯 Precisión del modelo: Próximamente

**Última actualización:** Hoy
            """.strip()
            
            await update.message.reply_text(
                status_message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in status_command: {e}", exc_info=True)
            await update.message.reply_text("❌ Error al obtener el estado. Por favor, inténtalo de nuevo.")
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle callback queries from inline keyboards.
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # TODO: Implement callback handlers on Día 3
            logger.info(f"Callback received: {query.data}")
            
        except Exception as e:
            logger.error(f"Error in callback_handler: {e}", exc_info=True)
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle non-command text messages.
        """
        try:
            user_message = update.message.text
            user_id = update.effective_user.id
            
            logger.info(f"Message from user {user_id}: {user_message[:50]}...")
            
            # Simple echo with suggestion
            await update.message.reply_text(
                "🤔 Para solicitar un análisis, usa el comando:\n"
                "`/analisis [equipo1] vs [equipo2]`\n\n"
                "Ejemplo: `/analisis Real Madrid vs Barcelona`",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Error in message_handler: {e}", exc_info=True)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle errors in bot updates.
        """
        logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
        
        # Notify user if possible
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde."
            )
    
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message to a specific chat.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Parse mode (Markdown, HTML, None)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")
            return False
    
    async def send_broadcast(self, chat_ids: list[int], text: str, parse_mode: str = "Markdown") -> Dict[str, int]:
        """
        Send broadcast message to multiple chats.
        
        Args:
            chat_ids: List of Telegram chat IDs
            text: Message text
            parse_mode: Parse mode
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0}
        
        for chat_id in chat_ids:
            success = await self.send_message(chat_id, text, parse_mode)
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            # Rate limiting: wait 0.1s between messages
            await asyncio.sleep(0.1)
        
        logger.info(f"Broadcast completed: {results['success']} success, {results['failed']} failed")
        return results
    
    def run(self) -> None:
        """
        Start the bot (blocking call).
        """
        logger.info("Starting Telegram bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def start_async(self) -> None:
        """
        Start the bot (async call).
        """
        logger.info("Starting Telegram bot (async)...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    async def stop(self) -> None:
        """
        Stop the bot gracefully.
        """
        logger.info("Stopping Telegram bot...")
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()