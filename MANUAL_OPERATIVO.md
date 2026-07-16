# 📋 Manual Operativo - Tipster IA Bot

Documento de referencia rápida: qué servicio hace qué, qué vas a tener que pagar más adelante, y qué se puede mejorar. Actualízalo cuando cambie algo importante.

---

## 📍 Dónde nos quedamos (última sesión: 2026-07-16)

**Contexto para retomar en otro PC / otra sesión con Claude:** este proyecto es un bot de Telegram (`@IdG_analisis_bot`) que da pronósticos de apuestas deportivas, con un canal gratis y un grupo VIP de pago vía Stripe. Está desplegado gratis en Render (Web Service, modo webhook) desde el repo de GitHub `cristobalsotoacosta03-dot/tipster-ai-bot`, rama `main`, con auto-deploy en cada push.

**Lo que se hizo en esta sesión (de cero a desplegado):**
- Se auditó el proyecto recién subido a GitHub y se encontraron/corrigieron bugs reales: `main.py` llamaba a un método bloqueante desde dentro de un event loop ya activo (crash garantizado), y el manejador de señales apuntaba a un método inexistente.
- Render eliminó el plan Free para "Background Worker" (mínimo $7/mes) — se migró el bot de modo *polling* a modo *webhook* (servidor `aiohttp` propio con `GET /`, `GET /health` y `POST /<token>`) para poder desplegar como **Web Service**, que sí tiene plan Free.
- Se cerró el flujo de negocio completo: `/start` registra usuario en BD, `/analisis` comprueba VIP real y límite diario gratuito (antes estaba todo hardcodeado/sin implementar), `/premium` genera checkout real de Stripe, y se añadió la ruta `POST /webhook/stripe` que activa el VIP automáticamente, guarda el pago, y genera una invitación real de un solo uso al grupo VIP vía API de Telegram (antes esto no existía / era un enlace falso).
- Se hizo `ANTHROPIC_API_KEY` opcional para poder lanzar sin pagar la API de Claude todavía — decisión de negocio: lanzar ya con picks manuales gratis + VIP de pago, invertir en la API de Claude solo cuando haya ventas VIP en cola.
- Se arreglaron 3 rondas de errores de build en Render: `upstash-redis==0.1.0` no existía en PyPI (fijado a `1.7.0`), `stripe==7.8.0` estaba yanked (fijado a `7.8.2`), y Render usaba Python 3.14 por defecto sin wheel para `pydantic-core` (fijado a `3.11.9` vía `.python-version`).
- Se limpiaron 4 archivos huérfanos en la raíz del repo (residuos de un merge conflict).
- **Confirmado funcionando:** build pasa en Render, `/start` responde bien en Telegram (probado con captura real), webhook de Stripe creado y con el `whsec_...` puesto en Render, Redis de Upstash creado y conectado, UptimeRobot con monitor a `/health` cada 5 min creado.

**Pendiente para la próxima sesión (en orden de prioridad):**
1. Confirmar que el bot es **admin del grupo VIP** con permiso de invitar usuarios — sin esto, el enlace de invitación tras el pago falla silenciosamente (queda en logs de Render).
2. Hacer un **pago de prueba real** en Stripe para validar de punta a punta que el webhook activa el VIP y llega la invitación al grupo.
3. Cuando haya ventas VIP encadenadas: comprar créditos reales en `console.anthropic.com` y sustituir el placeholder `sk-ant-api03-PENDIENTE_DE_VALIDACION` en `ANTHROPIC_API_KEY` (Render → Environment).
4. Antes de escalar con clientes de pago reales: resolver que la base de datos SQLite no es persistente en el plan Free de Render (se borra en cada redeploy) — subir a Starter o migrar a un Postgres externo gratuito.

Ver también el checklist al final de este documento.

**Reorganización del repositorio (2026-07-16):** se limpió la raíz y `docs/` para que no queden documentos contradictorios entre sí. `PROJECT_STATUS.md` (que llevaba desde el Día 1 sin actualizar y contradecía este manual) se eliminó — este archivo es ahora la única fuente de estado real. Los documentos técnicos se agruparon en `docs/technical/`, la guía de deploy paso a paso se movió a `docs/deployment/DEPLOY_NOW.md`, y todo el material del sprint inicial (plan y logs diarios) se archivó en `docs/archive/` como contexto histórico — con un aviso en `day_07_summary.md` porque esa sección de "resultados de lanzamiento" es una simulación, no datos reales. Índice completo en [`docs/README.md`](docs/README.md). Se dejó también fijada en `docs/marketing/tiktok_ads_plan.md` la regla de negocio: no se invierte en publicidad hasta 10 clientes VIP de pago.

---

## 🗂️ Qué aplicación se usa para cada cosa

| Servicio | Para qué | Dónde entrar |
|---|---|---|
| **GitHub** | Guarda el código del bot. Cada `git push` a `main` dispara un redeploy automático en Render. | github.com/cristobalsotoacosta03-dot/tipster-ai-bot |
| **Render.com** | Aloja el bot 24/7 (plan Free, Web Service en modo webhook). Aquí están TODAS las variables de entorno (keys). | dashboard.render.com → tipster-ia-bot → Environment |
| **BotFather (Telegram)** | Crea y administra el bot (@IdG_analisis_bot). Aquí se saca el `TELEGRAM_BOT_TOKEN`. | Chat con @BotFather → `/mybots` |
| **Anthropic Console** | API de Claude (el motor de IA para `/analisis`). Distinto de tu suscripción Claude Pro. | console.anthropic.com → API Keys / Billing |
| **Stripe** | Cobra las suscripciones VIP y avisa al bot cuando alguien paga (webhook). | dashboard.stripe.com → Payments / Webhooks |
| **Upstash** | Redis gratuito, cachea los análisis para no repetir llamadas caras a Claude. | console.upstash.com |
| **UptimeRobot** | Hace ping a `/health` cada 5 min para que Render no duerma el servicio. | dashboard.uptimerobot.com |
| **API-Football** | Datos/estadísticas de partidos que alimentan el análisis. | api-football.com → Dashboard |

---

## 💰 Qué es gratis ahora vs qué vas a tener que pagar

| Concepto | Estado actual | Cuándo pagar / cuánto |
|---|---|---|
| Hosting (Render) | Gratis (Web Service Free) | $7/mes (Starter) si necesitas disco persistente o quitar el "arranque en frío" del todo |
| Telegram Bot API | Gratis siempre | Nunca cuesta |
| **Claude API (Anthropic)** | **Desactivada** (key placeholder, `/analisis` responde "disponible muy pronto") | De pago por uso, aparte de Claude Pro. Cárgalo cuando tengas ventas VIP en cola — con ~$5-10 de crédito inicial vas sobrado para probar |
| Stripe | Gratis crear cuenta y cobrar | Comisión automática (~1.4% + 0.25€) por cada cobro exitoso. No hay que hacer nada, se descuenta solo |
| Upstash Redis | Gratis (tier free) | Solo si superas el límite del tier free (revisar en su dashboard si crece mucho el uso) |
| API-Football | Gratis (100 req/día) | Si necesitas más de 100 consultas/día, hay planes de pago |
| UptimeRobot | Gratis (1 monitor de 50 disponibles) | Solo si quieres monitorizar más cosas o intervalos más cortos que 5 min |

**Resumen: hoy el único coste real pendiente es la API de Claude, y solo cuando decidas activarla.**

---

## ⚠️ Limitaciones actuales / cosas a mejorar

1. **Tiempo de respuesta tras inactividad**: aunque UptimeRobot le hace ping cada 5 min para evitar que Render duerma el servicio (los Web Services free se duermen a los 15 min sin tráfico), no está 100% garantizado que nunca haya un "arranque en frío" de 30-60s. Si notas al bot lento tras un rato sin uso, esto es lo que pasa. Se soluciona del todo solo pagando el plan Starter.

2. **Base de datos NO persistente**: el plan Free de Render no permite disco persistente. Esto significa que si haces un redeploy (o Render reinicia el servicio por lo que sea), **se borran los usuarios, el estado VIP y el historial de pagos** de la base de datos SQLite. Mientras tengas pocos usuarios de prueba no pasa nada, pero **antes de tener varios clientes de pago reales, hay que resolver esto**: opción A) pagar Starter ($7/mes) para tener disco; opción B) migrar esos datos a una base externa gratuita (ej. Postgres en Supabase o Neon). Avísame cuando quieras hacer esto.

3. **`/analisis` deshabilitado**: hasta que no pongas una `ANTHROPIC_API_KEY` real (con crédito) en Render, esa función solo muestra "disponible muy pronto". No bloquea nada más del bot.

4. **El bot necesita ser admin del grupo VIP**: para poder generar automáticamente el enlace de invitación cuando alguien paga. Si no lo es, el pago se procesa igual pero el usuario no recibirá el enlace (queda en los logs de Render como error). Revisa que ya lo hayas configurado.

5. **Contenido 100% manual por ahora**: el bot no publica nada solo en el canal gratis ni en el grupo VIP — eso lo escribes y publicas tú directamente desde Telegram. Si en el futuro quieres que el bot publique picks automáticamente, habría que construir esa función.

6. **Cancelación de suscripción**: el bot está preparado para revocar el VIP automáticamente si alguien cancela en Stripe (`customer.subscription.deleted`), pero esa parte del flujo aún no se ha probado con un pago/cancelación real.

---

## 🔧 Cómo hacer cambios

- Cualquier cambio de código → `git push` a `main` en GitHub → Render lo detecta y redeploya solo (2-3 min).
- Ver logs en vivo: Render Dashboard → tipster-ia-bot → pestaña **Logs**.
- Cambiar una variable de entorno (key, precio, etc.): Render → **Environment** → editar → guardar (redeploya solo).

---

## ✅ Checklist de lanzamiento

- [x] Bot desplegado en Render (gratis, modo webhook)
- [x] `/start`, `/help`, `/status` funcionando
- [x] `/premium` genera checkout real de Stripe
- [x] Webhook de Stripe configurado y apuntando a `/webhook/stripe`
- [x] UptimeRobot monitorizando `/health`
- [ ] Bot confirmado como admin del grupo VIP (con permiso de invitar)
- [ ] Primer pago de prueba en Stripe (modo test o real) para validar que el VIP se activa solo
- [ ] `ANTHROPIC_API_KEY` real añadida cuando decidas invertir en IA
- [ ] Migrar base de datos a almacenamiento persistente antes de escalar con clientes reales
