# 🚀 Guía de Despliegue - Tipster IA Bot

Guía completa para desplegar el bot en producción usando Render.com.

## 📋 Requisitos Previos

- Cuenta en [Render.com](https://render.com/)
- Repositorio en GitHub/GitLab
- API keys configuradas (Anthropic, Stripe, API-Football)
- Grupo VIP de Telegram creado

## 🏗️ Opciones de Despliegue

### Opción 1: Render.com (Recomendado)

**Ventajas:**
- ✅ Tier gratuito disponible
- ✅ Deploy automático desde Git
- ✅ SSL automático
- ✅ Escalabilidad automática
- ✅ Logs integrados

**Pasos:**

1. **Preparar el repositorio**
```bash
# Asegúrate de que todo está commiteado
git add .
git commit -m "feat: ready for production deployment"
git push origin main
```

2. **Crear servicio en Render**

   a. Ve a https://dashboard.render.com/
   b. Click en "New +" → "Background Worker"
   c. Conecta tu repositorio de GitHub/GitLab
   d. Configura el servicio:

   **Configuración Básica:**
   - **Name:** `tipster-ia-bot`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Plan:** `Free` (o `Starter` para producción)

   **Variables de Entorno:**
   ```
   TELEGRAM_BOT_TOKEN=tu_token_aquí
   TELEGRAM_ADMIN_ID=tu_id_aquí
   TELEGRAM_VIP_GROUP_ID=-100xxxxxxxxxx
   ANTHROPIC_API_KEY=sk-ant-api03-...
   STRIPE_API_KEY=sk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PRICE_ID_MONTHLY=price_...
   STRIPE_PRICE_ID_YEARLY=price_...
   API_FOOTBALL_KEY=...
   UPSTASH_REDIS_REST_URL=...
   UPSTASH_REDIS_REST_TOKEN=...
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   CACHE_TTL_HOURS=6
   MAX_ANALYSIS_PER_DAY=100
   FREE_TIPS_PER_DAY=2
   VIP_MONTHLY_PRICE_EUR=29.99
   VIP_YEARLY_PRICE_EUR=299.00
   CURRENCY=EUR
   ```

3. **Deploy**
   - Click en "Create Background Worker"
   - Render clonará tu repo, instalará dependencias y desplegará
   - El deploy tomará ~2-3 minutos
   - Podrás ver los logs en tiempo real

4. **Verificar deployment**
   ```bash
   # En los logs de Render deberías ver:
   ✅ Sistema inicializado correctamente
   ✅ Claude API conectado correctamente
   ✅ Bot de Telegram inicializado
   🚀 Iniciando bot...
   ```

### Opción 2: Railway.app

**Ventajas:**
- ✅ $5 crédito gratuito mensual
- ✅ Deploy desde Git
- ✅ Fácil configuración

**Pasos:**

1. Conecta tu repo en https://railway.app/
2. Configura las variables de entorno
3. Deploy automático

### Opción 3: VPS (DigitalOcean, AWS, etc.)

**Para usuarios avanzados:**

```bash
# En tu VPS
git clone <tu-repo-url>
cd tipster-ia-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus credenciales
python main.py

# Usar systemd para mantenerlo corriendo
sudo nano /etc/systemd/system/tipster-bot.service
```

**Archivo de servicio systemd:**
```ini
[Unit]
Description=Tipster IA Bot
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/home/tu_usuario/tipster-ia-bot
ExecStart=/home/tu_usuario/tipster-ia-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tipster-bot
sudo systemctl start tipster-bot
sudo systemctl status tipster-bot
```

## 🔧 Configuración de Stripe

### 1. Crear Productos y Precios

1. Ve a https://dashboard.stripe.com/products
2. Crea dos productos:

**Producto 1: Suscripción Mensual**
- Nombre: "Tipster IA VIP - Mensual"
- Precio: €29.99/mes
- Tipo: Recurring

**Producto 2: Suscripción Anual**
- Nombre: "Tipster IA VIP - Anual"
- Precio: €299/año
- Tipo: Recurring

3. Copia los Price IDs:
   - `price_xxx` (mensual)
   - `price_yyy` (anual)

### 2. Configurar Webhook

1. Ve a https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. URL del webhook: `https://tu-dominio.com/webhook/stripe`
4. Eventos a escuchar:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copia el webhook secret: `whsec_xxx`

### 3. Obtener API Keys

1. Ve a https://dashboard.stripe.com/apikeys
2. Copia:
   - Secret key (modo test primero): `sk_test_xxx`
   - Luego cambia a live: `sk_live_xxx`

## 📱 Configuración de Telegram

### 1. Crear Bot

1. Abre Telegram y busca @BotFather
2. Envía `/newbot`
3. Sigue las instrucciones
4. Copia el token: `123456:ABC-DEF...`

### 2. Obtener tu User ID

1. Busca @userinfobot
2. Envía `/start`
3. Copia tu User ID: `123456789`

### 3. Crear Grupo VIP

1. Crea un grupo de Telegram
2. Añade @BotFather como administrador
3. Añade tu bot como administrador
4. Obtén el Group ID:
   - Añade @getidsbot al grupo
   - Envía un mensaje
   - Copia el Group ID: `-1001234567890`

### 4. Configurar Bot en Grupo

1. Ve a @BotFather
2. Envía `/setcommands`
3. Selecciona tu bot
4. Pega estos comandos:
```
start - Inicia el bot
help - Guía de comandos
analisis - Análisis de partido
premium - Plan VIP
status - Estado del servicio
```

## 🗄️ Configuración de Redis (Upstash)

1. Ve a https://upstash.com/
2. Crea una cuenta gratuita
3. Crea un nuevo Redis database
4. Copia:
   - REST URL: `https://tu-redis.upstash.io`
   - REST Token: `tu-token-aquí`

## 📊 Monitoreo

### Logs en Render

1. Ve a tu servicio en Render
2. Click en "Logs"
3. Podrás ver logs en tiempo real

### Métricas Importantes

```python
# Monitorear estos valores:
- Uso de API de Anthropic (tokens/día)
- Número de análisis generados
- Tasa de error
- Tiempo de respuesta promedio
- Costes diarios
```

### Alertas Recomendadas

Configura alertas para:
- Bot caído (sin logs por >5 minutos)
- Uso de API > 80% del presupuesto
- Tasa de error > 5%
- Memoria > 90%

## 🔄 Actualizaciones

### Deploy Automático (Recomendado)

Configura auto-deploy en Render:
1. Ve a tu servicio
2. Settings → Auto-Deploy
3. Activa "Auto-Deploy on push to main"
4. Ahora cada push a `main` desplegará automáticamente

### Deploy Manual

```bash
# Si necesitas forzar un deploy
git commit --allow-empty -m "trigger deploy"
git push origin main
```

## 🐛 Troubleshooting

### Bot no responde

1. Verifica logs en Render
2. Asegúrate de que el token de Telegram es correcto
3. Verifica que el bot tiene permisos en el grupo VIP

### Errores de Claude API

1. Verifica tu API key de Anthropic
2. Revisa tu saldo en https://console.anthropic.com/
3. Verifica límites de rate

### Errores de Stripe

1. Verifica que usas el webhook secret correcto
2. Asegúrate de que los Price IDs son correctos
3. Verifica que el modo (test/live) es consistente

### Alto consumo de memoria

1. Activa cache de Redis
2. Reduce `MAX_ANALYSIS_PER_DAY`
3. Considera upgrade de plan en Render

## 📈 Escalabilidad

### Cuando escalar

- **> 100 usuarios activos/día:** Considera plan Starter en Render
- **> 500 análisis/día:** Aumenta límites de API
- **> 1000 usuarios:** Migra a VPS o Kubernetes

### Optimizaciones

1. **Cache agresivo:** Cachear análisis por 12-24 horas
2. **Colas de procesamiento:** Usar Redis Queue para análisis
3. **Base de datos:** Añadir PostgreSQL para persistencia
4. **CDN:** Para servir contenido estático

## 🔒 Seguridad en Producción

### Checklist Pre-Launch

- [ ] Variables de entorno configuradas
- [ ] API keys en modo production (no test)
- [ ] Webhook secrets configurados
- [ ] Bot con permisos limitados
- [ ] Logs sin información sensible
- [ ] Rate limiting activo
- [ ] Backup de base de datos configurado
- [ ] Monitoreo activo

### Mejores Prácticas

1. **Nunca** commitees `.env` a Git
2. **Rota** API keys cada 90 días
3. **Monitorea** costes de API diariamente
4. **Backup** de datos críticos semanalmente
5. **Actualiza** dependencias mensualmente

## 📞 Soporte

Si tienes problemas con el deployment:

1. Revisa los logs en Render
2. Consulta la documentación de Render: https://render.com/docs
3. Verifica el estado de servicios: https://status.render.com

---

**Última actualización:** Día 1 del Sprint - 15/07/2026
**Versión:** 1.0.0