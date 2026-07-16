# 📚 Documentación de API - Tipster IA Bot

Documentación técnica de la arquitectura API y endpoints del sistema.

## 🏗️ Arquitectura General

```
┌─────────────┐
│   Usuario   │
│  Telegram   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Telegram Bot   │
│  (python-telegram-bot)
└──────┬──────────┘
       │
       ├──────────────────┐
       ▼                  ▼
┌─────────────┐   ┌──────────────┐
│   Claude    │   │   Stats      │
│     AI      │   │   Fetcher    │
│  (Anthropic)│   │  (API-Football)
└─────────────┘   └──────────────┘
       │                  │
       │                  ▼
       │          ┌──────────────┐
       │          │    Cache     │
       │          │   (Redis)    │
       │          └──────────────┘
       │
       ▼
┌─────────────┐
│  Stripe     │
│  Payments   │
└─────────────┘
```

## 🔌 Componentes Principales

### 1. Telegram Bot (`src/bot/telegram_bot.py`)

**Clase:** `TelegramBot`

**Responsabilidades:**
- Gestión de conexión con Telegram API
- Registro de handlers de comandos
- Envío de mensajes y broadcasts
- Manejo de callbacks y errores

**Métodos Principales:**

```python
# Inicialización
bot = TelegramBot()

# Comandos disponibles
/start - Mensaje de bienvenida
/help - Guía de comandos
/analisis [equipo1] vs [equipo2] - Análisis de partido
/premium - Información VIP
/status - Estado del servicio

# Métodos públicos
await bot.send_message(chat_id, text, parse_mode="Markdown")
await bot.send_broadcast(chat_ids, text, parse_mode="Markdown")
bot.run()  # Iniciar bot (blocking)
await bot.start_async()  # Iniciar bot (async)
await bot.stop()  # Detener bot
```

### 2. Claude Client (`src/analyzer/claude_client.py`)

**Clase:** `ClaudeClient`

**Responsabilidades:**
- Comunicación con Anthropic API
- Gestión de prompts y respuestas
- Retry logic y manejo de errores
- Health checks

**Métodos Principales:**

```python
# Inicialización
client = ClaudeClient()

# Análisis de partido
analysis = await client.analyze_match(
    prompt="datos del partido...",
    system_prompt="prompt personalizado (opcional)",
    max_tokens=4096
)

# Health check
is_healthy = await client.health_check()
```

**Configuración:**
- Modelo: `claude-3-5-sonnet-20241022`
- Max tokens: 4096
- Temperature: 0.7
- Retry: 3 intentos con backoff exponencial

### 3. Settings (`config/settings.py`)

**Clase:** `Settings`

**Variables de Entorno:**

```python
# Telegram
telegram_bot_token: str
telegram_admin_id: int
telegram_vip_group_id: int

# Anthropic
anthropic_api_key: str

# Stripe
stripe_api_key: str
stripe_webhook_secret: str
stripe_price_id_monthly: str
stripe_price_id_yearly: str

# API de Datos
api_football_key: Optional[str]

# Cache
upstash_redis_rest_url: Optional[str]
upstash_redis_rest_token: Optional[str]

# Aplicación
environment: str = "development"
log_level: str = "INFO"
cache_ttl_hours: int = 6
max_analysis_per_day: int = 50
free_tips_per_day: int = 2

# Monetización
vip_monthly_price_eur: float = 29.99
vip_yearly_price_eur: float = 299.00
currency: str = "EUR"
```

## 🔄 Flujos de Datos

### Flujo 1: Análisis de Partido

```
Usuario envía: /analisis Real Madrid vs Barcelona
         │
         ▼
TelegramBot.analisis_command()
         │
         ▼
Validar límites de usuario (free vs VIP)
         │
         ▼
StatsFetcher.obtener_datos_partido(equipos)
         │
         ▼
PromptEngine.generar_prompt(datos_partido)
         │
         ▼
ClaudeClient.analyze_match(prompt)
         │
         ▼
Formatear respuesta para Telegram
         │
         ▼
Enviar análisis al usuario
```

### Flujo 2: Sistema de Pagos

```
Usuario solicita acceso VIP
         │
         ▼
TelegramBot.premium_command()
         │
         ▼
Mostrar opciones de pago
         │
         ▼
Usuario selecciona plan
         │
         ▼
Stripe checkout session
         │
         ▼
Webhook de Stripe confirma pago
         │
         ▼
PaymentHandler.activar_suscripcion(usuario)
         │
         ▼
AccessControl.otorgar_acceso_vip(usuario)
         │
         ▼
Enviar invitación al grupo VIP
```

## 📡 API Endpoints (Futuro - Día 4+)

### REST API para Dashboard

```
GET  /api/v1/health - Health check
GET  /api/v1/stats - Estadísticas del servicio
GET  /api/v1/users - Lista de usuarios (admin)
GET  /api/v1/analyses - Análisis generados (admin)
POST /api/v1/broadcast - Enviar mensaje masivo (admin)
```

### Webhooks

```
POST /webhook/stripe - Webhook de Stripe para pagos
POST /webhook/telegram - Webhook de Telegram (alternativa a polling)
```

## 🗄️ Modelos de Datos

### Usuario

```python
class User:
    user_id: int              # Telegram user ID
    username: str             # @username
    first_name: str           # Nombre
    last_name: str            # Apellidos
    is_vip: bool              # Es usuario VIP
    vip_start_date: datetime  # Inicio de suscripción
    vip_end_date: datetime    # Fin de suscripción
    analyses_today: int       # Análisis usados hoy
    last_analysis_date: date  # Último día de uso
    created_at: datetime      # Fecha de registro
    updated_at: datetime      # Última actualización
```

### Análisis

```python
class Analysis:
    id: str                   # UUID único
    user_id: int              # Usuario que solicitó
    match_data: dict          # Datos del partido
    prompt: str               # Prompt enviado a Claude
    response: str             # Respuesta de Claude
    tokens_used: int          # Tokens consumidos
    cost_eur: float           # Coste en euros
    created_at: datetime      # Fecha de creación
    cached: bool              # ¿Venía de cache?
```

### Pago

```python
class Payment:
    id: str                   # Stripe payment intent ID
    user_id: int              # Usuario
    amount_eur: float         # Cantidad pagada
    currency: str             # EUR
    status: str               # pending/completed/failed
    subscription_type: str    # monthly/yearly
    stripe_customer_id: str   # Stripe customer ID
    created_at: datetime
```

## 🔒 Seguridad

### Autenticación

- **Telegram:** Validación de webhook signatures (futuro)
- **Stripe:** Verificación de webhook signatures
- **API Keys:** Rotación cada 90 días
- **Admin:** Whitelist de Telegram IDs

### Rate Limiting

```python
# Límites por usuario
FREE_USER:
  - 2 análisis/día
  - 1 request/segundo

VIP_USER:
  - Análisis ilimitados
  - 5 requests/segundo

GLOBAL:
  - 100 requests/minuto
  - 1000 requests/día
```

### Validación de Datos

- Todos los inputs son validados con Pydantic
- Sanitización de texto para prevenir inyecciones
- Límites de longitud en mensajes
- Filtrado de caracteres especiales

## 📊 Monitoreo

### Métricas a Recolectar

```python
# Métricas de uso
- total_users
- active_users_24h
- vip_subscriptions
- analyses_generated
- cache_hit_rate
- api_calls_per_day

# Métricas de rendimiento
- avg_response_time
- error_rate
- uptime_percentage
- token_usage_per_analysis

# Métricas de negocio
- revenue_per_day
- conversion_rate
- churn_rate
- customer_lifetime_value
```

### Logs

```python
# Niveles de log
DEBUG - Detalles técnicos para desarrollo
INFO  - Eventos importantes del sistema
WARNING - Situaciones anómalas no críticas
ERROR - Errores recuperables
CRITICAL - Errores fatales
```

## 🚀 Despliegue

### Variables de Entorno en Producción

```env
ENVIRONMENT=production
LOG_LEVEL=WARNING
CACHE_TTL_HOURS=6
MAX_ANALYSIS_PER_DAY=100
FREE_TIPS_PER_DAY=2
```

### Escalabilidad

**Horizontal:**
- Múltiples instancias del bot detrás de un load balancer
- Redis compartido para cache
- Base de datos centralizada (PostgreSQL)

**Vertical:**
- Aumentar límites de API según demanda
- Cache más agresivo en horas pico
- Colas de procesamiento para análisis

## 🔧 Mantenimiento

### Tareas Programadas

```python
# Diarias
- Limpiar logs antiguos (>7 días)
- Resetear contadores de análisis diarios
- Generar reporte de métricas

# Semanales
- Backup de base de datos
- Análisis de tendencias
- Revisión de costes de API

# Mensuales
- Facturación de suscripciones
- Rotación de API keys
- Auditoría de seguridad
```

### Comandos de Admin

```
/admin stats - Ver estadísticas
/admin broadcast [mensaje] - Enviar mensaje a todos
/admin cache clear - Limpiar cache
/admin maintenance on/off - Modo mantenimiento
```

## 📝 Notas de Desarrollo

### Convenciones de Código

- **PEP 8** para estilo Python
- **Type hints** en todas las funciones
- **Docstrings** en formato Google
- **Async/await** para operaciones I/O
- **Logging** estructurado con niveles apropiados

### Testing

```python
# Estructura de tests
tests/
├── unit/
│   ├── test_claude_client.py
│   ├── test_telegram_bot.py
│   └── test_prompt_engine.py
├── integration/
│   ├── test_analysis_flow.py
│   └── test_payment_flow.py
└── fixtures/
    └── sample_data.json
```

### CI/CD (Futuro)

```yaml
# .github/workflows/ci.yml
- Lint (flake8, black)
- Test (pytest)
- Security scan (bandit)
- Deploy to staging
- Manual approval
- Deploy to production
```

---

**Última actualización:** Día 1 del Sprint - 15/07/2026
**Versión:** 1.0.0
**Mantenido por:** Equipo de Desarrollo Tipster IA