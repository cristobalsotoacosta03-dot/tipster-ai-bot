# 🤖 Tipster IA Bot

Servicio de análisis de apuestas deportivas impulsado por Claude AI. Análisis táctico-profesional con estadísticas avanzadas para maximizar el value betting a largo plazo.

## 📋 Características

- **Análisis Inteligente:** Evaluación profunda de partidos usando Claude 3.5 Sonnet
- **Estadísticas Avanzadas:** xG, PPDA, progresión ofensiva, eficiencia defensiva
- **Análisis Táctico:** Sistemas de juego, pressing, transiciones, construcción de juego
- **Sistema de Monetización:** Plan gratuito + VIP con acceso a grupo exclusivo
- **Automatización Completa:** Desde el análisis hasta el cobro y acceso automático

## 🏗️ Arquitectura

```
tipster-ia-bot/
├── src/
│   ├── bot/                    # Lógica del bot de Telegram
│   │   ├── telegram_bot.py    # Conexión y comandos de Telegram
│   │   └── formatters.py      # Formateo de análisis
│   ├── analyzer/               # Motor de análisis con Claude
│   │   ├── claude_client.py   # Cliente de Anthropic API
│   │   ├── prompt_engine.py   # Generación de prompts tácticos
│   │   └── match_analyzer.py  # Orquestación de análisis
│   ├── data/                   # Fuentes de datos
│   │   ├── stats_fetcher.py   # Obtención de estadísticas
│   │   ├── cache_manager.py   # Cache para optimizar costes
│   │   └── database.py        # Gestión de base de datos
│   └── monetization/           # Sistema de pagos
│       ├── payment_handler.py # Gestión de suscripciones
│       └── access_control.py  # Control de acceso VIP
├── config/
│   └── settings.py            # Configuración general
├── tests/
├── .env.example
├── requirements.txt
├── render.yaml
└── main.py                     # Punto de entrada
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- Cuenta en [Anthropic Console](https://console.anthropic.com/) (API key)
- Cuenta en [Telegram](https://telegram.org/) (Bot token via @BotFather)
- Cuenta en [Stripe](https://stripe.com/) (para pagos)
- Cuenta en [API-Football](https://www.api-football.com/) (estadísticas)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/cristobalsotoacosta03-dot/tipster-ai-bot.git
cd tipster-ai-bot
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env  # o usa tu editor preferido
```

5. **Ejecutar el bot**
```bash
python main.py
```

## 📝 Configuración

Edita el archivo `.env` con tus credenciales:

```env
# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_ADMIN_ID=123456789
TELEGRAM_VIP_GROUP_ID=-1001234567890

# Anthropic
ANTHROPIC_API_KEY=sk-ant-api03-...

# Stripe
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_MONTHLY=price_...
STRIPE_PRICE_ID_YEARLY=price_...

# API de Datos
API_FOOTBALL_KEY=...

# Redis (opcional, para cache)
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
```

## 🎯 Comandos del Bot

- `/start` - Mensaje de bienvenida
- `/help` - Guía de comandos
- `/analisis [equipo1] vs [equipo2]` - Análisis completo del partido
- `/premium` - Información sobre plan VIP
- `/status` - Estado del servicio

## 💰 Modelo de Monetización

### Plan Gratuito
- 2 análisis gratuitos por día
- Tips básicos en canal público
- Contenido educativo

### Plan VIP - €29.99/mes
- Análisis diarios de 3-5 partidos seleccionados
- Pronósticos con stake recomendado (1-5 unidades)
- Análisis táctico avanzado y estadísticas métricas
- Acceso al grupo VIP de Telegram exclusivo
- Seguimiento en vivo de picks
- Historial de resultados y estadísticas de acierto
- Soporte prioritario

**Plan Anual:** €299/año (ahorra 2 meses)

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.11+
- **IA:** Anthropic API (Claude 3.5 Sonnet)
- **Bot:** python-telegram-bot v20+
- **Datos:** API-Football / API-Sports
- **Pagos:** Stripe
- **Cache:** Redis (Upstash)
- **Deploy:** Render.com
- **Logs:** Colorlog con salida a archivo

## 📊 Sprint de 7 Días

### Día 1: Fundación Técnica ✅
- [x] Estructura de proyecto
- [x] Configuración de entorno
- [x] Bot básico de Telegram
- [x] Cliente de Claude API
- [x] Sistema de logging

### Día 2: Motor de Análisis ✅
- [x] Fetcher de estadísticas deportivas
- [x] Prompt maestro de análisis
- [x] Sistema de cache
- [x] Análisis end-to-end

### Día 3: Lógica del Bot ✅
- [x] Comandos completos
- [x] Sistema de suscripciones
- [x] Integración Stripe
- [x] Acceso a grupo VIP

### Día 4: Testing y Pulido ✅
- [x] Testing completo (46 tests)
- [x] Optimización de costes
- [x] Manejo de errores
- [x] Deploy inicial

### Día 5: Contenido y Marketing ✅
- [x] Estrategia de contenido
- [x] Plan de lanzamiento
- [x] Material de marketing

### Día 6: Lanzamiento 🚀
- [ ] Publicar videos en redes
- [ ] Activar campaña de captación
- [ ] Primeros envíos de análisis
- [ ] Monitoreo 24/7

### Día 7: Optimización
- [ ] Análisis de métricas
- [ ] Mejoras basadas en feedback
- [ ] Escalar capacidad
- [ ] Plan semana 2

## 🎨 Prompt de Análisis

El sistema utiliza un prompt maestro especializado que incluye:

1. **Contextualización:** Liga, momento de temporada, motivación
2. **Análisis Táctico:** Sistemas de juego, pressing, transiciones
3. **Estadísticas Avanzadas:** xG, PPDA, progresión ofensiva
4. **Factores Ambientales:** Cancha, clima, ambiente
5. **Lesiones/Sanciones:** Impacto en rendimiento
6. **Pronóstico:** Con stake recomendado (1-5 unidades)
7. **Justificación Técnica:** Razonamiento detallado

## 📈 Métricas de Éxito

- Bot funcionando 24/7 sin caídas
- 100+ miembros en canal gratuito (Semana 1)
- 10-20 clientes de pago (Semana 1)
- 5 videos con 1K+ visualizaciones totales
- ROI positivo desde día 1

## 🔒 Seguridad

- Nunca commitees el archivo `.env` a Git
- Usa variables de entorno para todas las credenciales
- Rota las API keys regularmente
- Implementa rate limiting en producción
- Monitorea el uso de API para control de costes

## 📝 Licencia

Este proyecto es privado y confidencial. Todos los derechos reservados.

## 👨‍💻 Autor

Desarrollado con ❤️ usando Claude AI

---

**¿Preguntas?** Contacta al equipo de desarrollo.