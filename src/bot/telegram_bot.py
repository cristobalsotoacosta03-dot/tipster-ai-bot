"""
Main Telegram Bot implementation.
Handles bot initialization, command routing, and message processing.
"""
import asyncio
from typing import Optional, Dict, Any
from aiohttp import web
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
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
from src.analyzer.match_analyzer import MatchAnalyzer
from src.bot.formatters import AnalysisFormatter

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram Bot wrapper for the Tipster IA service.
    Handles all bot operations including commands, callbacks, and messages.
    """

    def __init__(self, database=None, access_control=None, payment_handler=None):
        """
        Initialize Telegram bot with token from settings.

        Args:
            database: DatabaseManager used to persist users/analyses.
            access_control: AccessControl used for VIP checks and free-tier limits.
            payment_handler: PaymentHandler used to create Stripe checkout
                sessions and process webhook events.
        """
        self.token = settings.telegram_bot_token
        self.admin_id = settings.telegram_admin_id
        self.vip_group_id = settings.telegram_vip_group_id

        self.database = database
        self.access_control = access_control
        self.payment_handler = payment_handler

        # Initialize analysis components
        self.match_analyzer = MatchAnalyzer()
        self.analysis_formatter = AnalysisFormatter()

        # Create application
        self.application = Application.builder().token(self.token).build()

        # Register handlers
        self._register_handlers()

        # Set when running in webhook mode; used by stop() to know how
        # to shut down cleanly.
        self._webhook_runner: Optional[web.AppRunner] = None

        logger.info("Telegram bot initialized with Match Analyzer")
    
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

            if self.database:
                self.database.create_or_update_user(
                    user_id=user_id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                )

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
        Perform complete match analysis using MatchAnalyzer.
        """
        try:
            user_id = update.effective_user.id
            
            # Check if user provided match info
            if not context.args or len(context.args) < 3:
                await update.message.reply_text(
                    "⚠️ **Uso incorrecto**\n\n"
                    "Formato: `/analisis [equipo1] vs [equipo2]`\n"
                    "Ejemplo: `/analisis Real Madrid vs Barcelona`\n\n"
                    "💡 *Necesitas mencionar ambos equipos separados por 'vs'*",
                    parse_mode="Markdown"
                )
                return
            
            # Enforce free-tier daily limit before doing any expensive work
            user_is_vip = False
            if self.access_control:
                user_is_vip = self.access_control.is_vip_user(user_id)
                limit_status = self.access_control.check_analysis_limit(user_id)
                if not limit_status["can_analyze"]:
                    await update.message.reply_text(
                        "🚫 **Límite diario alcanzado**\n\n"
                        f"Has usado tus {limit_status['analyses_limit']} análisis gratuitos de hoy.\n"
                        "Usa /premium para acceso VIP ilimitado, o vuelve mañana.",
                        parse_mode="Markdown"
                    )
                    return

            # Parse match query
            match_query = " ".join(context.args)
            logger.info(f"Analysis request from user {user_id}: {match_query}")

            # Send "analyzing" message
            status_message = await update.message.reply_text(
                "🔍 **Analizando partido...**\n\n"
                "⏳ Esto puede tardar 10-20 segundos\n"
                "📊 Consultando estadísticas\n"
                "🧠 Generando análisis táctico\n\n"
                "Por favor, espera...",
                parse_mode="Markdown"
            )
            
            # Parse teams (simple parsing - would be more robust in production)
            teams = match_query.split(" vs ")
            if len(teams) != 2:
                await status_message.edit_text(
                    "⚠️ **Formato incorrecto**\n\n"
                    "Usa: `/analisis [equipo1] vs [equipo2]`\n"
                    "Ejemplo: `/analisis Real Madrid vs Barcelona`",
                    parse_mode="Markdown"
                )
                return
            
            home_team = teams[0].strip()
            away_team = teams[1].strip()

            # Perform analysis
            analysis_result = await self.match_analyzer.analyze_match(
                home_team=home_team,
                away_team=away_team,
                analysis_type="full" if user_is_vip else "express"
            )

            if not analysis_result:
                await status_message.edit_text(
                    "❌ **Error al obtener el análisis**\n\n"
                    "No pude encontrar datos para este partido.\n"
                    "Prueba con otros equipos o inténtalo más tarde.",
                    parse_mode="Markdown"
                )
                return
            
            # Format analysis for Telegram
            formatted_message = self.analysis_formatter.format_analysis_for_telegram(
                analysis_result,
                user_is_vip=user_is_vip
            )
            
            # Delete status message and send analysis
            await status_message.delete()
            
            # Send analysis (may need to split if too long)
            if len(formatted_message) > 4000:
                # Split into multiple messages
                parts = self._split_message(formatted_message, 4000)
                for part in parts:
                    await update.message.reply_text(part, parse_mode="Markdown")
            else:
                await update.message.reply_text(formatted_message, parse_mode="Markdown")

            if self.access_control and not user_is_vip:
                self.access_control.increment_analysis_count(user_id)

            if self.database:
                self.database.save_analysis({
                    "user_id": user_id,
                    "match_id": analysis_result.get("match_id"),
                    "home_team": home_team,
                    "away_team": away_team,
                    "analysis_type": analysis_result.get("analysis_type"),
                    "analysis": analysis_result.get("analysis"),
                    "match_data": analysis_result.get("match_data"),
                    "prompt_used": analysis_result.get("prompt_used"),
                    "from_cache": analysis_result.get("from_cache", False),
                })

            logger.info(f"Analysis sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in analisis_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Error al procesar el análisis. Por favor, inténtalo de nuevo."
            )
    
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

🎯 *El value betting es a largo plazo. Confía en el proceso.*
            """.strip()

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Mensual - €29.99", callback_data="checkout:monthly")],
                [InlineKeyboardButton("📆 Anual - €299 (ahorra 2 meses)", callback_data="checkout:yearly")],
            ])

            await update.message.reply_text(
                premium_message,
                parse_mode="Markdown",
                reply_markup=keyboard if self.payment_handler else None,
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

            logger.info(f"Callback received: {query.data}")

            if query.data and query.data.startswith("checkout:"):
                await self._handle_checkout_callback(query)

        except Exception as e:
            logger.error(f"Error in callback_handler: {e}", exc_info=True)

    async def _handle_checkout_callback(self, query) -> None:
        """
        Handle a "checkout:<monthly|yearly>" callback: create a Stripe
        Checkout session and send the payment link to the user.
        """
        if not self.payment_handler:
            await query.message.reply_text(
                "❌ El sistema de pagos no está disponible ahora mismo. Inténtalo más tarde."
            )
            return

        price_type = query.data.split(":", 1)[1]
        user = query.from_user

        session = await asyncio.to_thread(
            self.payment_handler.create_checkout_session,
            user_id=user.id,
            username=user.username,
            price_type=price_type,
            bot_username=self.application.bot.username,
        )

        if not session:
            await query.message.reply_text(
                "❌ No se pudo crear el enlace de pago. Inténtalo de nuevo en unos minutos."
            )
            return

        label = "mensual" if price_type == "monthly" else "anual"
        await query.message.reply_text(
            f"💳 **Suscripción {label} - Tipster IA VIP**\n\n"
            f"Completa tu pago aquí:\n{session['url']}\n\n"
            "Una vez confirmado el pago, tu acceso VIP se activará automáticamente "
            "y recibirás el enlace al grupo exclusivo.",
            parse_mode="Markdown",
        )
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle non-command text messages.
        """
        try:
            user_message = update.message.text
            user_id = update.effective_user.id
            
            logger.info(f"Message from user {user_id}: {user_message[:50]}...")
            
            # Check if message looks like a match query
            if " vs " in user_message.lower() or " vs." in user_message.lower():
                # Suggest using /analisis command
                await update.message.reply_text(
                    "💡 **¿Quieres analizar ese partido?**\n\n"
                    "Usa el comando:\n"
                    "`/analisis " + user_message + "`\n\n"
                    "Ejemplo: `/analisis " + user_message + "`",
                    parse_mode="Markdown"
                )
            else:
                # Default response
                await update.message.reply_text(
                    "🤔 Para solicitar un análisis, usa el comando:\n"
                    "`/analisis [equipo1] vs [equipo2]`\n\n"
                    "Ejemplo: `/analisis Real Madrid vs Barcelona`\n\n"
                    "O escribe directamente: `Real Madrid vs Barcelona`",
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
            error_message = "❌ Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde."
            
            # Try to get more specific error message
            if context.error:
                error_type = str(context.error).lower()
                if "rate limit" in error_type:
                    error_message = "⚠️ Demasiadas solicitudes. Por favor, espera un momento."
                elif "timeout" in error_type:
                    error_message = "⏱️ Tiempo de espera agotado. Inténtalo de nuevo."
            
            await update.effective_message.reply_text(error_message)
    
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
    
    async def start_polling(self) -> None:
        """
        Start the bot in long-polling mode (non-blocking: returns once
        polling has started, the Application keeps running in the
        background event loop). Used for local development.
        """
        logger.info("Starting Telegram bot (polling)...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    async def start_webhook(self, listen: str, port: int, webhook_url: str, url_path: str) -> None:
        """
        Start the bot in webhook mode (non-blocking) using a small aiohttp
        server instead of PTB's built-in webhook server, so we control the
        routes directly: POST /<url_path> receives Telegram updates and
        GET /, /health answer Render's health checks. Used in production,
        since Render's free plan only exists for Web Services, which must
        bind to $PORT and respond over HTTP.
        """
        logger.info(f"Starting Telegram bot (webhook) on {listen}:{port}...")
        await self.application.initialize()
        await self.application.start()
        await self.application.bot.set_webhook(
            url=f"{webhook_url}/{url_path}",
            allowed_updates=Update.ALL_TYPES,
        )

        async def handle_webhook(request: web.Request) -> web.Response:
            data = await request.json()
            update = Update.de_json(data, self.application.bot)
            await self.application.update_queue.put(update)
            return web.Response(status=200)

        async def handle_health(request: web.Request) -> web.Response:
            return web.Response(status=200, text="OK")

        app = web.Application()
        app.router.add_post(f"/{url_path}", handle_webhook)
        app.router.add_get("/", handle_health)
        app.router.add_get("/health", handle_health)

        if self.payment_handler:
            app.router.add_post("/webhook/stripe", self._handle_stripe_webhook)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, listen, port)
        await site.start()
        self._webhook_runner = runner
        logger.info(f"Webhook server listening on {listen}:{port}")

    async def _handle_stripe_webhook(self, request: web.Request) -> web.Response:
        """
        Handle Stripe webhook events (POST /webhook/stripe): verify the
        signature, process the event, and on a successful checkout grant
        VIP access + notify the user with the VIP group invite link.
        """
        payload = await request.read()
        signature = request.headers.get("Stripe-Signature", "")

        event = await asyncio.to_thread(
            self.payment_handler.handle_webhook, payload, signature
        )

        if not event:
            # Invalid signature or unhandled event type — Stripe doesn't
            # need to know the difference, just that we didn't 5xx.
            return web.Response(status=200)

        if event["event"] == "checkout_completed":
            await self._activate_vip_from_payment(event)
        elif event["event"] == "subscription_deleted":
            await self._deactivate_vip_from_subscription(event)

        return web.Response(status=200)

    async def _activate_vip_from_payment(self, event: Dict[str, Any]) -> None:
        """Grant VIP access after a successful Stripe checkout."""
        user_id = event.get("user_id")
        if not user_id:
            logger.error(f"Checkout completed without a user_id in metadata: {event}")
            return

        price_type = event.get("price_type", "monthly")
        duration_days = 365 if price_type == "yearly" else 30

        if self.access_control:
            self.access_control.grant_vip_access(
                user_id=user_id,
                username=event.get("username") or "",
                subscription_type=price_type,
                duration_days=duration_days,
            )

        if self.database:
            self.database.save_payment({
                "user_id": user_id,
                "stripe_payment_id": event.get("subscription_id"),
                "stripe_customer_id": event.get("customer_id"),
                "amount_eur": event.get("amount_total", 0.0),
                "status": "succeeded",
                "subscription_type": price_type,
            })
            if event.get("customer_id"):
                self.database.set_stripe_customer_id(user_id, event["customer_id"])

        invite_link = await self._create_vip_invite_link(user_id)
        message = (
            "🎉 **¡Bienvenido al plan VIP!**\n\n"
            f"Tu suscripción {price_type} está activa. Ya tienes acceso ilimitado a análisis.\n"
        )
        if invite_link:
            message += f"\n👉 Únete al grupo VIP: {invite_link}"

        await self.send_message(user_id, message)
        logger.info(f"VIP activated for user {user_id} ({price_type})")

    async def _create_vip_invite_link(self, user_id: int) -> Optional[str]:
        """
        Create a real, single-use Telegram invite link to the VIP group.
        Requires the bot to be an admin of `vip_group_id` with permission
        to invite users.
        """
        try:
            invite = await self.application.bot.create_chat_invite_link(
                chat_id=self.vip_group_id,
                member_limit=1,
                name=f"VIP-{user_id}",
            )
            return invite.invite_link
        except Exception as e:
            logger.error(f"Error creating VIP invite link for user {user_id}: {e}", exc_info=True)
            return None

    async def _deactivate_vip_from_subscription(self, event: Dict[str, Any]) -> None:
        """Revoke VIP access when a Stripe subscription is cancelled."""
        customer_id = event.get("customer_id")
        if not self.database or not customer_id:
            return

        user = self.database.get_user_by_stripe_customer_id(customer_id)
        if not user:
            logger.warning(f"Subscription deleted for unknown Stripe customer {customer_id}")
            return

        user_id = user["user_id"]
        if self.access_control:
            self.access_control.revoke_vip_access(user_id)
        elif self.database:
            self.database.update_vip_status(user_id=user_id, is_vip=False)

        await self.send_message(
            user_id,
            "ℹ️ Tu suscripción VIP ha finalizado. Puedes renovarla en cualquier momento con /premium."
        )
        logger.info(f"VIP revoked for user {user_id} (Stripe customer {customer_id})")

    async def stop(self) -> None:
        """
        Stop the bot gracefully.
        """
        logger.info("Stopping Telegram bot...")
        try:
            # Close match analyzer components
            if hasattr(self, 'match_analyzer'):
                await self.match_analyzer.stats_fetcher.close()
        except Exception as e:
            logger.error(f"Error closing components: {e}")

        if self._webhook_runner is not None:
            await self.application.bot.delete_webhook()
            await self._webhook_runner.cleanup()
        elif self.application.updater is not None and self.application.updater.running:
            await self.application.updater.stop()

        await self.application.stop()
        await self.application.shutdown()
    
    def _split_message(self, message: str, max_length: int = 4000) -> list[str]:
        """
        Split long message into multiple parts.
        
        Args:
            message: Message to split
            max_length: Maximum length per part
            
        Returns:
            List of message parts
        """
        parts = []
        current_part = ""
        
        for line in message.split('\n'):
            if len(current_part) + len(line) + 1 <= max_length:
                current_part += line + '\n'
            else:
                if current_part:
                    parts.append(current_part)
                current_part = line + '\n'
        
        if current_part:
            parts.append(current_part)
        
        return parts
