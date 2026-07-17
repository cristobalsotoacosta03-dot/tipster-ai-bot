# Tipster IA Bot

Servicio de análisis de apuestas deportivas con Claude AI. Bot de Telegram con plan gratuito + VIP (Stripe).

> **Estado real del proyecto** (qué está hecho, qué falta): [`MANUAL_OPERATIVO.md`](MANUAL_OPERATIVO.md).  
> Índice de docs: [`docs/README.md`](docs/README.md).  
> Política de IA: [`PRINCIPIOS_IA.md`](PRINCIPIOS_IA.md).

## Estado actual (resumen)

| Componente | Estado |
|---|---|
| Bot Telegram | En línea (Render, webhook) |
| Claude AI | Conectado |
| API de datos | Configurada |
| Stripe VIP | Configurado |
| Canales Telegram | Creados (gratis + VIP) |
| `/analisis` | Pendiente de cerrar |

## Características

- Análisis con Claude y estadísticas avanzadas (xG, PPDA, etc.)
- Plan free (límites diarios) + VIP con grupo exclusivo
- Checkout Stripe y activación automática de acceso
- Deploy en Render con auto-deploy desde GitHub

## Arquitectura

```
tipster-ia-bot/
├── src/
│   ├── bot/           # Telegram (comandos, formatters)
│   ├── analyzer/      # Claude, prompts, orquestación
│   ├── data/          # Stats, cache, BD
│   ├── monetization/  # Stripe, control de acceso
│   └── utils/
├── config/settings.py
├── tests/
├── docs/              # Técnica, deploy, marketing
├── main.py
└── render.yaml
```

## Inicio rápido (desarrollo local)

**Requisitos:** Python 3.11+, tokens de Telegram, Anthropic, Stripe, API-Football.

```bash
git clone https://github.com/cristobalsotoacosta03-dot/tipster-ai-bot.git
cd tipster-ai-bot

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # rellenar credenciales
python main.py
```

Variables principales: ver `.env.example` (`TELEGRAM_*`, `ANTHROPIC_API_KEY`, `STRIPE_*`, `API_FOOTBALL_KEY`, Redis opcional).

## Comandos del bot

| Comando | Descripción |
|---|---|
| `/start` | Bienvenida y registro |
| `/help` | Guía |
| `/analisis [eq1] vs [eq2]` | Análisis (en desarrollo) |
| `/premium` | Plan VIP / checkout |
| `/status` | Estado del servicio |

## Monetización

- **Gratis:** límites diarios + canal público  
- **VIP:** €29.99/mes (o anual con descuento) — análisis ampliados + grupo VIP  

## Stack

Python 3.11 · Anthropic Claude · python-telegram-bot · API-Football · Stripe · Redis (Upstash) · Render

## Seguridad

- No commitear `.env`
- Credenciales solo por variables de entorno
- Rate limiting y control de costes de API en producción

## Licencia

Proyecto privado. Todos los derechos reservados.
