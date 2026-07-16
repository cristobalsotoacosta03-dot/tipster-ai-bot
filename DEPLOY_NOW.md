# 🚀 DEPLOY EN PRODUCCIÓN - GUÍA EJECUTABLE

Guía paso a paso para desplegar Tipster IA Bot en Render.com **AHORA**.

---

## ⚡ PASO 1: Preparar Repositorio (5 minutos)

### 1.1 Verificar que todo está commiteado

```bash
cd tipster-ia-bot

# Ver estado de git
git status

# Si hay archivos sin commitear:
git add .
git commit -m "feat: ready for production deployment"
git push origin main
```

### 1.2 Verificar rama principal

```bash
# Asegúrate de estar en main/master
git branch

# Si estás en master, renombrar a main (opcional pero recomendado):
git branch -M main
git push origin main
```

---

## ⚡ PASO 2: Crear Cuenta en Render (2 minutos)

1. Ve a https://render.com/
2. Click en **"Get Started"**
3. Regístrate con **GitHub** (recomendado) o email
4. Autoriza Render para acceder a tus repositorios

---

## ⚡ PASO 3: Crear Servicio en Render (10 minutos)

### 3.1 Iniciar deployment

1. En el dashboard de Render, click en **"New +"** (esquina superior derecha)
2. Selecciona **"Background Worker"**
3. Click en **"Connect a repository"**
4. Selecciona tu repositorio `tipster-ia-bot`
5. Click en **"Connect"**

### 3.2 Configurar servicio

**Configuración básica:**

| Campo | Valor |
|-------|-------|
| **Name** | `tipster-ia-bot` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python main.py` |
| **Plan** | `Free` (para testing) o `Starter ($7/mes)` (para producción) |

**IMPORTANTE:** 
- Si usas plan Free, el bot se "duerme" después de 15 minutos de inactividad
- Para producción 24/7, usa plan **Starter ($7/mes)**

### 3.3 Configurar variables de entorno

Scroll down hasta **"Environment Variables"** y añade estas variables:

#### Variables Requeridas:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=tu_token_de_botfather
TELEGRAM_ADMIN_ID=tu_user_id_numérico
TELEGRAM_VIP_GROUP_ID=-100xxxxxxxxxx

# Anthropic (Claude AI)
ANTHROPIC_API_KEY=sk-ant-api03-tu_key_aquí

# Stripe (Pagos)
STRIPE_API_KEY=sk_live_tu_key_aquí
STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_secret
STRIPE_PRICE_ID_MONTHLY=price_xxx
STRIPE_PRICE_ID_YEARLY=price_yyy

# API Football (Estadísticas)
API_FOOTBALL_KEY=tu_api_key_aquí

# Redis Cache (Upstash)
UPSTASH_REDIS_REST_URL=https://tu-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=tu_token_upstash
```

#### Variables Opcionales (con valores por defecto):

```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
CACHE_TTL_HOURS=6
MAX_ANALYSIS_PER_DAY=100
FREE_TIPS_PER_DAY=2

# Monetization
VIP_MONTHLY_PRICE_EUR=29.99
VIP_YEARLY_PRICE_EUR=299.00
CURRENCY=EUR
```

**Cómo obtener cada API key:**

📱 **Telegram Bot Token:**
1. Abre Telegram, busca @BotFather
2. Envía `/newbot`
3. Sigue instrucciones, copia el token

👤 **Telegram Admin ID:**
1. Busca @userinfobot
2. Envía `/start`
3. Copia tu ID numérico

💬 **Telegram VIP Group ID:**
1. Crea grupo de Telegram
2. Añade @getidsbot al grupo
3. Envía un mensaje
4. Copia el ID (formato: `-1001234567890`)

🧠 **Anthropic API Key:**
1. Ve a https://console.anthropic.com/
2. Crea cuenta
3. Ve a "API Keys" → "Create Key"
4. Copia la key (formato: `sk-ant-api03-...`)

💳 **Stripe Keys:**
1. Ve a https://dashboard.stripe.com/apikeys
2. Copia "Secret key" (modo live: `sk_live_...`)
3. Ve a https://dashboard.stripe.com/products
4. Crea producto mensual (€29.99/mes) → copia Price ID
5. Crea producto anual (€299/año) → copia Price ID
6. Ve a https://dashboard.stripe.com/webhooks
7. Crea webhook endpoint (ver Paso 4)
8. Copia webhook secret (`whsec_...`)

⚽ **API Football Key:**
1. Ve a https://www.api-football.com/
2. Regístrate (plan gratuito disponible)
3. Ve a "Dashboard" → "API Key"
4. Copia tu key

🗄️ **Redis (Upstash):**
1. Ve a https://upstash.com/
2. Crea cuenta gratuita
3. Click "Create Redis database"
4. Copia:
   - REST URL: `https://xxx.upstash.io`
   - REST Token: `tu-token`

### 3.4 Configurar disco persistente

1. Scroll down hasta **"Disk"**
2. Click en **"Add Disk"**
3. Configura:
   - **Name:** `tipster-data`
   - **Mount Path:** `/opt/render/project/src/data`
   - **Size:** `1 GB`
4. Click **"Save"**

**Nota:** Esto es necesario para que la base de datos SQLite persista entre deployments.

---

## ⚡ PASO 4: Configurar Webhook de Stripe (5 minutos)

### 4.1 Obtener URL de tu bot

Después de crear el servicio en Render, obtendrás una URL como:
```
https://tipster-ia-bot.onrender.com
```

### 4.2 Crear webhook endpoint

1. Ve a https://dashboard.stripe.com/webhooks
2. Click en **"Add endpoint"**
3. **Endpoint URL:** `https://tu-app.onrender.com/webhook/stripe`
4. **Events to listen to:**
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
5. Click **"Add endpoint"**
6. Copia el **"Signing secret"** (formato: `whsec_...`)
7. Añade este valor a las variables de entorno en Render como `STRIPE_WEBHOOK_SECRET`

---

## ⚡ PASO 5: Deploy Inicial (3 minutos)

### 5.1 Iniciar deployment

1. En la página de configuración de Render, scroll hasta el final
2. Click en **"Create Background Worker"**
3. Render comenzará el deployment automáticamente

### 5.2 Monitorear deployment

Verás el progreso en tiempo real:
```
Building... (1-2 minutos)
  ✓ Cloning repository
  ✓ Installing dependencies
  ✓ Building image

Deploying... (30 segundos)
  ✓ Starting service
  ✓ Health check passed
```

### 5.3 Verificar logs

1. Click en la pestaña **"Logs"**
2. Deberías ver algo como:

```
============================================================
🤖 TIPSTER IA BOT - Inicializando sistema
============================================================
🧠 Inicializando cliente de Claude AI...
🔍 Verificando conexión con Claude API...
✅ Claude API conectado correctamente
🗄️  Inicializando base de datos...
✅ Base de datos conectada correctamente
🔐 Inicializando control de acceso...
✅ Control de acceso VIP inicializado
📱 Inicializando bot de Telegram...
✅ Bot de Telegram inicializado
============================================================
✅ Sistema inicializado correctamente
============================================================
🚀 Iniciando bot...
```

✅ **Si ves estos logs, el deploy fue exitoso!**

---

## ⚡ PASO 6: Verificar Funcionamiento (5 minutos)

### 6.1 Probar bot en Telegram

1. Abre Telegram
2. Busca tu bot por username
3. Envía `/start`
4. Deberías recibir mensaje de bienvenida

### 6.2 Probar comando de análisis

1. Envía `/analisis`
2. El bot debería pedirte un partido
3. Prueba con: `Real Madrid vs Barcelona`
4. Espera 10-20 segundos
5. Deberías recibir el análisis completo

### 6.3 Verificar base de datos

En los logs de Render, busca:
```
✅ Base de datos conectada correctamente
```

### 6.4 Verificar cache

En los logs deberías ver:
```
✅ Cache manager inicializado (Redis)
```

---

## ⚡ PASO 7: Configurar Auto-Deploy (2 minutos)

### 7.1 Activar auto-deploy

1. Ve a tu servicio en Render
2. Click en **"Settings"**
3. Scroll hasta **"Auto-Deploy"**
4. Activa **"Auto-Deploy on push to main"**
5. Click **"Save"**

### 7.2 Probar auto-deploy

```bash
# Hacer un cambio menor
cd tipster-ia-bot
echo "# Deploy test" >> README.md
git add README.md
git commit -m "test: auto-deploy"
git push origin main
```

3. Ve a Render, deberías ver un nuevo deployment iniciado automáticamente

---

## ✅ CHECKLIST DE VERIFICACIÓN

Marca cada item cuando lo completes:

### Pre-Deploy
- [ ] Código commiteado y pusheado a GitHub
- [ ] Cuenta en Render creada
- [ ] Repositorio conectado a Render
- [ ] Variables de entorno configuradas
- [ ] Disco persistente configurado (1GB)

### APIs Externas
- [ ] Telegram Bot Token obtenido
- [ ] Telegram Admin ID obtenido
- [ ] Telegram VIP Group ID obtenido
- [ ] Anthropic API Key obtenida
- [ ] Stripe Secret Key (modo live) obtenida
- [ ] Stripe Price IDs (mensual y anual) obtenidos
- [ ] Stripe Webhook Secret obtenido
- [ ] API Football Key obtenida
- [ ] Upstash Redis configurado

### Deployment
- [ ] Servicio creado en Render
- [ ] Build command configurado
- [ ] Start command configurado
- [ ] Variables de entorno añadidas
- [ ] Disco persistente montado
- [ ] Deployment iniciado
- [ ] Logs verificados (sin errores)
- [ ] Bot responde en Telegram
- [ ] Comando /analisis funciona
- [ ] Auto-deploy activado

### Post-Deploy
- [ ] Monitoreo configurado (logs activos)
- [ ] Alertas configuradas (opcional)
- [ ] Documentación actualizada con URL de producción
- [ ] Equipo notificado del lanzamiento

---

## 🐛 TROUBLESHOOTING COMÚN

### Error: "Module not found"

**Solución:**
```bash
# Verifica que requirements.txt está en la raíz
# Verifica que el build command es correcto:
pip install -r requirements.txt
```

### Error: "TELEGRAM_BOT_TOKEN not found"

**Solución:**
1. Ve a Render → Tu servicio → Environment
2. Verifica que `TELEGRAM_BOT_TOKEN` está definida
3. Asegúrate de que no hay espacios extra

### Error: "Claude API connection failed"

**Solución:**
1. Verifica tu API key en https://console.anthropic.com/
2. Asegúrate de que tienes saldo disponible
3. Verifica que la key empieza por `sk-ant-api03-`

### Bot no responde en Telegram

**Solución:**
1. Verifica logs en Render
2. Asegúrate de que el bot tiene permisos en el grupo VIP
3. Verifica que el token es correcto
4. Prueba con `/start` en chat privado primero

### Error: "Database is locked"

**Solución:**
1. Verifica que el disco persistente está montado en `/opt/render/project/src/data`
2. Reinicia el servicio en Render

### Alto consumo de memoria

**Solución:**
1. Activa cache de Redis (verifica variables UPSTASH_*)
2. Reduce `MAX_ANALYSIS_PER_DAY` a 50
3. Considera upgrade a plan Starter

---

## 📊 MONITOREO POST-DEPLOY

### Métricas a monitorear diariamente:

```bash
# En Render → Logs, verificar:
✅ Sin errores críticos
✅ Tiempo de respuesta < 30 segundos
✅ Uso de API Claude < 80% del presupuesto
✅ Cache hit rate > 70%
✅ Sin caídas del servicio
```

### Alertas recomendadas:

Configura en Render → Settings → Alerts:
- **Service Down:** Si no hay logs por >5 minutos
- **High Memory:** Si memoria > 90%
- **High CPU:** Si CPU > 80%

---

## 🎯 PRÓXIMOS PASOS DESPUÉS DEL DEPLOY

1. **Probar en producción** (1 hora)
   - [ ] Probar todos los comandos
   - [ ] Verificar pagos con Stripe (modo test primero)
   - [ ] Probar acceso VIP

2. **Configurar canal de captura** (2 horas)
   - Crear canal Telegram público
   - Configurar bot como admin
   - Crear contenido de bienvenida

3. **Preparar lanzamiento** (1 día)
   - Crear 10 videos TikTok/Reels
   - Programar posts en redes
   - Configurar analytics

4. **Lanzar!** (Fin de semana)
   - Publicar primer video
   - Invitar primeros usuarios
   - Monitorear métricas

---

## 💡 CONSEJOS FINALES

1. **Plan Free vs Starter:**
   - Free: Para testing, se duerme después de 15 min
   - Starter ($7/mes): Para producción 24/7

2. **Modo Test vs Live en Stripe:**
   - Primero prueba en modo TEST
   - Cuando todo funcione, cambia a LIVE

3. **Backups:**
   - Render hace backups automáticos
   - Exporta base de datos semanalmente

4. **Escalado:**
   - Empieza con plan Free/Starter
   - Escala a Standard ($25/mes) cuando tengas >100 usuarios/día

---

## 🆘 SOPORTE

Si tienes problemas:

1. **Render Docs:** https://render.com/docs
2. **Render Status:** https://status.render.com
3. **Render Community:** https://community.render.com

---

## 🎉 FELICITACIONES!

Una vez completados todos los pasos, tu bot estará:
- ✅ Desplegado en producción 24/7
- ✅ Funcionando en Telegram
- ✅ Procesando pagos con Stripe
- ✅ Cacheando análisis para reducir costes
- ✅ Listo para captar clientes

**Tu bot ya está generando valor. Ahora a vender!** 🚀

---

**Tiempo total estimado:** 30-45 minutos  
**Dificultad:** Media  
**Costo inicial:** $0 (plan Free) o $7/mes (plan Starter)

**Siguiente paso:** Crear contenido para lanzamiento (ver `docs/marketing/content_strategy.md`)