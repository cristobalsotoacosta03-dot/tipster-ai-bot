# 🚀 DEPLOY EN PRODUCCIÓN - GUÍA EJECUTABLE (PLAN GRATUITO)

Guía paso a paso para desplegar Tipster IA Bot en Render.com **SIN INVERSIÓN INICIAL**.

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
| **Plan** | `Free` (SIN INVERSIÓN - recomendado para empezar) |

**IMPORTANTE - PLAN GRATUITO:**
- ✅ El bot se "duerme" después de 15 minutos de inactividad
- ✅ Se despierta automáticamente cuando llega un nuevo mensaje
- ✅ Perfecto para testing y lanzamiento inicial
- ⚠️ Primer request después de dormir tarda 30-60 segundos
- 💡 **Truco:** Usa UptimeRobot (gratis) para mantenerlo despierto 24/7

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

### 3.4 Configurar disco persistente (OPCIONAL en plan Free)

1. Scroll down hasta **"Disk"**
2. Click en **"Add Disk"**
3. Configura:
   - **Name:** `tipster-data`
   - **Mount Path:** `/opt/render/project/src/data`
   - **Size:** `1 GB`
4. Click **"Save"**

**Nota:** 
- En plan Free, el disco persiste pero el servicio se duerme
- La base de datos SQLite se mantiene entre deployments
- Para producción 24/7, considera upgrade a plan Starter ($7/mes)

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
4. Espera 10-20 segundos (30-60s si el bot estaba dormido)
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

## ⚡ PASO 7: Configurar UptimeRobot para mantener bot despierto (5 minutos)

### 7.1 Por qué necesitas UptimeRobot

En plan Free, Render duerme el bot después de 15 minutos de inactividad. UptimeRobot hace ping cada 5 minutos para mantenerlo despierto 24/7.

### 7.2 Configurar UptimeRobot

1. Ve a https://uptimerobot.com/
2. Click en **"Sign Up"** (plan gratuito)
3. Crea cuenta con email o Google
4. Una vez dentro, click en **"Add New Monitor"**

### 7.3 Configurar monitor

**Monitor Type:** HTTP(s)

**Configuración:**
- **Monitor Name:** `Tipster IA Bot`
- **URL (or IP):** `https://tu-app.onrender.com/health`
  - Reemplaza `tu-app` con el nombre de tu app en Render
  - Ejemplo: `https://tipster-ia-bot.onrender.com/health`
- **Monitoring Interval:** `5 minutes`
- **Monitor Timeout:** `30 seconds`

**Notification Settings:**
- **Send notification when monitor goes down:** ✅ Activado
- **Send notification when monitor comes back up:** ✅ Activado
- **Notification Email:** tu-email@ejemplo.com

**Advanced Settings:**
- **HTTP Method:** GET
- **Keyword Type:** Does not contain
- **Keyword:** (dejar vacío)

5. Click en **"Create Monitor"**

### 7.4 Verificar funcionamiento

1. Espera 5-10 minutos
2. UptimeRobot hará el primer ping
3. Verifica en Render → Logs que hay actividad
4. El bot ahora estará despierto 24/7

### 7.5 Límites del plan Free de UptimeRobot

- ✅ 50 monitores gratuitos
- ✅ Intervalo mínimo: 5 minutos
- ✅ Notificaciones por email
- ✅ Dashboard web
- ⚠️ Solo 1 monitor necesario para este bot

---

## ✅ CHECKLIST DE VERIFICACIÓN

Marca cada item cuando lo completes:

### Pre-Deploy
- [ ] Código commiteado y pusheado a GitHub
- [ ] Cuenta en Render creada
- [ ] Repositorio conectado a Render
- [ ] Variables de entorno configuradas
- [ ] Disco persistente configurado (1GB) - OPCIONAL

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
- [ ] Servicio creado en Render (plan Free)
- [ ] Build command configurado
- [ ] Start command configurado
- [ ] Variables de entorno añadidas
- [ ] Disco persistente montado (opcional)
- [ ] Deployment iniciado
- [ ] Logs verificados (sin errores)
- [ ] Bot responde en Telegram
- [ ] Comando /analisis funciona
- [ ] UptimeRobot configurado

### Post-Deploy
- [ ] UptimeRobot funcionando (bot despierto 24/7)
- [ ] Monitoreo activo
- [ ] Primer análisis de prueba exitoso
- [ ] Documentación actualizada con URL de producción

---

## 🐛 TROUBLESHOOTING COMÚN (PLAN FREE)

### Bot se duerme y tarda en responder

**Solución:**
1. Configura UptimeRobot para hacer ping cada 5 minutos
2. URL a monitorear: `https://tu-app.onrender.com/health`
3. Esto mantendrá el bot despierto 24/7

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
2. Asegúrate de que tienes saldo disponible (mínimo $5)
3. Verifica que la key empieza por `sk-ant-api03-`

### Bot no responde en Telegram (plan Free)

**Solución:**
1. Verifica logs en Render
2. El bot puede estar "dormido" - espera 30-60 segundos
3. Asegúrate de que el bot tiene permisos en el grupo VIP
4. Verifica que el token es correcto
5. Prueba con `/start` en chat privado primero

### Error: "Database is locked"

**Solución:**
1. Verifica que el disco persistente está montado en `/opt/render/project/src/data`
2. Reinicia el servicio en Render
3. En plan Free, esto es normal después de que el bot se "despierte"

### Alto consumo de memoria

**Solución:**
1. Activa cache de Redis (verifica variables UPSTASH_*)
2. Reduce `MAX_ANALYSIS_PER_DAY` a 50
3. En plan Free, Render limita memoria a 512MB

---

## 📊 MONITOREO POST-DEPLOY (PLAN FREE)

### Métricas a monitorear diariamente:

```bash
# En Render → Logs, verificar:
✅ Sin errores críticos
✅ Tiempo de respuesta 30-60 segundos (primera request después de dormir)
✅ Uso de API Claude < 80% del presupuesto diario
✅ Cache hit rate > 70% (para reducir costes)
✅ Bot se despierta correctamente después de inactividad
```

### Alertas recomendadas (GRATIS):

**UptimeRobot (Recomendado)**
1. Ve a https://uptimerobot.com/
2. Crea cuenta gratuita
3. Añade monitor HTTP(s):
   - URL: `https://tu-app.onrender.com/health`
   - Intervalo: 5 minutos
   - Notificación: Email o Telegram
4. Esto te alertará si el bot se cae

**Render Alerts (Opcional)**
Configura en Render → Settings → Alerts:
- **Service Down:** Si no hay logs por >15 minutos
- **High Memory:** Si memoria > 90%

---

## 🎯 PRÓXIMOS PASOS DESPUÉS DEL DEPLOY (SIN INVERSIÓN)

1. **Probar en producción** (1 hora)
   - [ ] Probar todos los comandos en Telegram
   - [ ] Verificar pagos con Stripe (modo TEST primero)
   - [ ] Probar acceso VIP
   - [ ] Configurar UptimeRobot para mantener bot despierto

2. **Configurar canal de captura** (2 horas)
   - Crear canal Telegram público
   - Configurar bot como admin
   - Crear contenido de bienvenida
   - Diseñar lead magnet (ej: "5 errores que te hacen perder en apuestas")

3. **Preparar lanzamiento** (1 día)
   - Crear 10 videos TikTok/Reels con el móvil
   - Editar videos con CapCut (gratis)
   - Programar posts en redes
   - Configurar analytics gratuitos (Google Analytics)

4. **Lanzar este fin de semana** (SIN INVERSIÓN)
   - Publicar primer video en TikTok/Instagram/YouTube Shorts
   - Compartir en grupos de fútbol y apuestas
   - Invitar primeros usuarios al canal de Telegram
   - Monitorear métricas y ajustar estrategia

5. **Cuando factures €500+** (Mes 1-2)
   - Upgrade a plan Starter ($7/mes) para 24/7
   - Invertir en publicidad pagada
   - Contratar editor de videos

---

## 💡 CONSEJOS FINALES - PLAN GRATUITO

### Cómo funciona el plan Free:

✅ **Ventajas:**
- $0 costo, sin inversión inicial
- Suficiente para testing y primeros usuarios
- Deploy automático desde Git
- SSL incluido
- 750 horas/mes (suficiente para 1 instancia 24/7 con UptimeRobot)

⚠️ **Limitaciones:**
- Se duerme después de 15 minutos de inactividad
- Primer request tarda 30-60 segundos en despertar
- No ideal para producción con muchos usuarios
- Memoria limitada a 512MB

### Estrategia para plan Free:

1. **Mantener el bot despierto:**
   - Usar UptimeRobot (gratis) para ping cada 5 minutos
   - URL: `https://tu-app.onrender.com/health`

2. **Optimizar para plan Free:**
   - Cache agresivo (12-24 horas) para reducir llamadas a Claude API
   - Limitar análisis a 50/día en desarrollo
   - Monitorear costes de API externas (Anthropic, API-Football)

3. **Cuándo upgrade a Starter ($7/mes):**
   - Cuando tengas >10 usuarios activos/día
   - Cuando el tiempo de respuesta de 30-60s sea problema
   - Cuando quieras 24/7 sin interrupciones
   - Cuando factures >€500/mes (el bot se paga solo)

### Modo Test vs Live en Stripe:

- Primero prueba en modo TEST (sin dinero real)
- Cuando todo funcione, cambia a LIVE
- En plan Free, puedes procesar pagos sin problemas

---

## 🎉 FELICITACIONES!

Una vez completados todos los pasos, tu bot estará:
- ✅ Desplegado en Render.com (plan Free - SIN INVERSIÓN)
- ✅ Funcionando en Telegram 24/7 (con UptimeRobot)
- ✅ Procesando pagos con Stripe
- ✅ Cacheando análisis para reducir costes
- ✅ Listo para captar clientes SIN GASTAR DINERO

**Tu bot ya está generando valor. Ahora a vender!** 🚀

---

### 💰 Costo Real del Plan Free:

- **Hosting:** $0/mes (Render Free tier)
- **Cache:** $0/mes (Upstash Free tier: 10,000 comandos/día)
- **Monitoreo:** $0 (UptimeRobot Free tier)
- **Dominio:** $0 (usar URL de Render)
- **Total:** **$0/mes** 🎉

### 📈 Cuándo invertir:

- **Mes 1-2:** Mantener plan Free, facturar €500+
- **Mes 3:** Upgrade a Starter ($7/mes) cuando tengas 20+ VIPs
- **Mes 4:** Invertir en publicidad con los beneficios del bot

---

**Tiempo total estimado:** 30-45 minutos  
**Dificultad:** Media  
**Costo inicial:** $0 (plan Free - SIN INVERSIÓN)

**Siguiente paso:** Crear contenido para lanzamiento (ver `docs/marketing/content_strategy.md`)