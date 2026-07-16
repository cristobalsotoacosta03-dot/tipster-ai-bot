# 📋 Manual Operativo - Tipster IA Bot

Documento de referencia rápida: qué servicio hace qué, qué vas a tener que pagar más adelante, y qué se puede mejorar. Actualízalo cuando cambie algo importante.

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
