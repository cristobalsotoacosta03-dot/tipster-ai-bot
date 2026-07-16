"""
Main entry point for Tipster IA Bot.
Initializes and starts the Telegram bot service.
"""
import asyncio
import os
import signal
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.utils.logger import logger
from src.bot.telegram_bot import TelegramBot
from src.analyzer.claude_client import ClaudeClient
from src.data.database import DatabaseManager
from src.monetization.access_control import AccessControl
from src.monetization.payment_handler import PaymentHandler


class TipsterIABot:
    """
    Main application class that orchestrates all components.
    """
    
    def __init__(self):
        """Initialize all components."""
        self.bot = None
        self.claude_client = None
        self.database = None
        self.access_control = None
        self.payment_handler = None
        self.running = False
        self._stop_event: asyncio.Event | None = None
        
        logger.info("=" * 60)
        logger.info("🤖 TIPSTER IA BOT - Inicializando sistema")
        logger.info("=" * 60)
    
    async def initialize(self) -> None:
        """Initialize all bot components."""
        try:
            # Initialize Claude client
            logger.info("🧠 Inicializando cliente de Claude AI...")
            self.claude_client = ClaudeClient()
            
            # Verify Claude API connection
            logger.info("🔍 Verificando conexión con Claude API...")
            claude_ok = await self.claude_client.health_check()
            if not claude_ok:
                logger.warning("⚠️  Claude API no disponible - El bot funcionará en modo limitado")
            else:
                logger.info("✅ Claude API conectado correctamente")
            
            # Initialize Database
            logger.info("🗄️  Inicializando base de datos...")
            self.database = DatabaseManager()
            db_ok = self.database.health_check()
            if not db_ok:
                logger.warning("⚠️  Base de datos no disponible - Datos no persistentes")
            else:
                logger.info("✅ Base de datos conectada correctamente")
            
            # Initialize Access Control
            logger.info("🔐 Inicializando control de acceso...")
            self.access_control = AccessControl(database=self.database)
            logger.info("✅ Control de acceso VIP inicializado")

            # Initialize Payment Handler
            logger.info("💳 Inicializando gestor de pagos...")
            self.payment_handler = PaymentHandler()
            logger.info("✅ Gestor de pagos inicializado")

            # Initialize Telegram bot
            logger.info("📱 Inicializando bot de Telegram...")
            self.bot = TelegramBot(
                database=self.database,
                access_control=self.access_control,
                payment_handler=self.payment_handler,
            )
            logger.info("✅ Bot de Telegram inicializado")
            
            logger.info("=" * 60)
            logger.info("✅ Sistema inicializado correctamente")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error durante la inicialización: {e}", exc_info=True)
            raise
    
    async def start(self) -> None:
        """Start the bot service."""
        try:
            await self.initialize()
            self.running = True
            
            logger.info("🚀 Iniciando bot...")
            
            # Setup graceful shutdown
            self._stop_event = asyncio.Event()
            self._setup_signal_handlers()

            # Render's free plan only exists for Web Services, which must
            # listen on $PORT and respond over HTTP. Render also sets
            # RENDER_EXTERNAL_URL automatically, so we use it to switch to
            # webhook mode there; locally (no PORT set) we fall back to
            # polling.
            port = os.environ.get("PORT")
            external_url = os.environ.get("RENDER_EXTERNAL_URL")
            if port and external_url:
                await self.bot.start_webhook(
                    listen="0.0.0.0",
                    port=int(port),
                    webhook_url=external_url,
                    url_path=settings.telegram_bot_token,
                )
            else:
                await self.bot.start_polling()

            logger.info("✅ Bot en ejecución")
            await self._stop_event.wait()
            await self.stop()

        except Exception as e:
            logger.error(f"❌ Error fatal: {e}", exc_info=True)
            await self.stop()
            sys.exit(1)
    
    async def stop(self) -> None:
        """Stop the bot service gracefully."""
        if not self.running:
            return
        
        logger.info("🛑 Deteniendo bot...")
        self.running = False
        
        try:
            if self.bot:
                await self.bot.stop()
            
            # Close database connections
            if self.database:
                # SQLite doesn't need explicit close, but good practice
                pass
            
            logger.info("✅ Bot detenido correctamente")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error durante el apagado: {e}", exc_info=True)
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, self._handle_stop_signal)
            logger.debug("Signal handlers configurados")
        except (NotImplementedError, RuntimeError):
            # Windows' default event loop doesn't support add_signal_handler
            logger.debug("Signal handlers no disponibles en este sistema")

    def _handle_stop_signal(self) -> None:
        """Triggered when SIGINT/SIGTERM is received."""
        logger.info("⚠️  Señal de apagado recibida")
        if self._stop_event:
            self._stop_event.set()


def main():
    """Main entry point."""
    try:
        # Print startup banner
        print("\n" + "=" * 60)
        print("🤖 TIPSTER IA BOT - Servicio de Análisis de Apuestas")
        print("=" * 60)
        print(f"🌍 Ambiente: {settings.environment}")
        print(f"📊 Log Level: {settings.log_level}")
        print("=" * 60 + "\n")
        
        # Create and start bot
        app = TipsterIABot()
        asyncio.run(app.start())
        
    except KeyboardInterrupt:
        print("\n⚠️  Bot detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()