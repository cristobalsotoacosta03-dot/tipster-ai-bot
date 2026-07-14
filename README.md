# Bot de tracking + IA para canal de análisis deportivo

Sistema de registro transparente de picks con estadísticas verificables en tiempo real,
más generación de razonamientos y contenido asistida por IA (Claude).

**Importante:** este sistema no predice resultados ni cuotas. Registra y explica
decisiones tomadas por un analista humano, y calcula estadísticas reales sobre
el histórico. Ver `docs/PRINCIPIOS_IA.md`.

## Estructura del proyecto

```
tipster-ai-bot/
├── bot/
│   └── main.py          # Bot de Telegram (aiogram) — comandos y flujo
├── backend/
│   ├── stats.py          # Cálculo de estadísticas (ROI, % acierto)
│   └── ai_engine.py       # Integración con Claude (razonamientos, contenido)
├── db/
│   ├── models.py          # Modelo de datos (SQLAlchemy)
│   └── database.py        # Conexión a la base de datos
├── docs/
│   └── PRINCIPIOS_IA.md   # Principios de uso de IA en el proyecto
├── requirements.txt
└── .env.example
```

## Arrancar en local

1. Instala Python 3.11+ y crea un entorno virtual:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Instala dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Copia `.env.example` a `.env` y rellena:
   - `TELEGRAM_BOT_TOKEN`: habla con [@BotFather](https://t.me/BotFather) en Telegram, crea un bot con `/newbot`, copia el token.
   - `ADMIN_TELEGRAM_IDS`: tu ID de Telegram (habla con [@userinfobot](https://t.me/userinfobot) para obtenerlo).
   - `ANTHROPIC_API_KEY`: consíguela en [console.anthropic.com](https://console.anthropic.com).
   - `DATABASE_URL`: déjalo vacío para usar SQLite local (cero configuración).

4. Carga las variables de entorno y arranca el bot:
   ```
   export $(cat .env | xargs)   # en Mac/Linux
   python bot/main.py
   ```

5. En Telegram, escribe `/start` a tu bot para comprobar que responde.

## Comandos disponibles (Fase 1)

| Comando | Quién | Qué hace |
|---|---|---|
| `/nuevopick` | Admin | Registra un pick paso a paso, genera razonamiento con IA y lo publica |
| `/resolver <id> <ganado\|perdido\|nulo>` | Admin | Marca un pick como resuelto y calcula unidades |
| `/stats [deporte]` | Todos | Muestra estadísticas reales (% acierto, ROI, unidades) |
| `/ultimos` | Todos | Muestra los últimos 5 picks publicados |

## Próximos pasos (Fase 2 y 3)

- Motor de comparación de cuotas entre casas (The Odds API) — ver `docs/ROADMAP.md`
- Generación de contenido multiformato (X, Reels) desde cada pick
- Gestión de suscripciones/pagos (Stripe) y salas segmentadas
- Dashboard web de estadísticas

## Despliegue en producción

Para producción se recomienda:
- Railway o Render (deploy directo desde GitHub, plan gratuito/barato suficiente para empezar)
- PostgreSQL gestionado (Railway y Render lo ofrecen integrado)
- Configurar las variables de entorno del `.env.example` en el panel del hosting
