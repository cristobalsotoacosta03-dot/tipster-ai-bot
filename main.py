"""
Main entry point for Tipster IA Bot.
Initializes and starts the Telegram bot service.
"""
import asyncio
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


class TipsterIABot:
    """
    Main application class that orchestrates all components.
    """
    
    def __init__(self):
        """Initialize all components."""
        self.bot: Optional[TelegramBot] = None
        self.claude_client: Optional[ClaudeClient] = None
        self.database: Optional[DatabaseManager] = None
        self.access_control: Optional[AccessControl] = None
        self.running = False
        
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
            self.access_control = AccessControl()
            logger.info("✅ Control de acceso VIP inicializado")
            
            # Initialize Telegram bot
            logger.info("📱 Inicializando bot de Telegram...")
            self.bot = TelegramBot()
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
            self._setup_signal_handlers()
            
            # Start bot (blocking)
            self.bot.run()
            
        except KeyboardInterrupt:
            logger.info("⚠️  Interrupción de teclado detectada")
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
            # Only works on Unix systems
            import signal
            for sig in (signal.SIGINT, signal.SIGTERM):
                signal.signal(sig, self._signal_handler)
            logger.debug("Signal handlers configurados")
        except (ImportError, OSError):
            # Windows doesn't support signal handlers the same way
            logger.debug("Signal handlers no disponibles en este sistema")


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