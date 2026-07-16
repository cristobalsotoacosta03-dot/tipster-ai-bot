# 📋 Manual Operativo - Tipster IA Bot

**Última actualización:** 16/07/2026 - 12:42  
**Actualizado por:** Tech Lead / Product Manager  
**Próxima sesión:** 17/07/2026 (Lanzamiento)

---

## 📍 Dónde nos quedamos (última sesión: 2026-07-16)

**Contexto para retomar en otro PC / otra sesión con Claude:** este proyecto es un bot de Telegram (`@IdG_analisis_bot`) que da pronósticos de apuestas deportivas, con un canal gratis y un grupo VIP de pago vía Stripe. Está desplegado gratis en Render (Web Service, modo webhook) desde el repo de GitHub `cristobalsotoacosta03-dot/tipster-ai-bot`, rama `main`, con auto-deploy en cada push.

### Lo que se hizo en esta sesión (de cero a desplegado):

1. **Auditoría y fixes iniciales:**
   - `main.py` llamaba a método bloqueante desde event loop (crash garantizado) → Corregido
   - Manejador de señales apuntaba a método inexistente → Corregido
   - 3 rondas de errores de build en Render solucionados

2. **Migración a modo webhook:**
   - Render eliminó plan Free para Background Worker
   - Se migró de polling a webhook (servidor aiohttp propio)
   - Rutas: `GET /`, `GET /health`, `POST /<token>`, `POST /webhook/stripe`

3. **Flujo de negocio completo cerrado:**
   - `/start` registra usuario en BD
   - `/analisis` comprueba VIP real y límite diario gratuito
   - `/premium` genera checkout real de Stripe
   - Webhook `/webhook/stripe` activa VIP automáticamente
   - Genera invitación real de un solo uso al grupo VIP

4. **Decisiones de negocio:**
   - `ANTHROPIC_API_KEY` desactivada (placeholder) → `/analisis` muestra "disponible muy pronto"
   - Decisión: lanzar con picks manuales gratis + VIP de pago
   - Invertir en Claude solo cuando haya ventas VIP en cola

5. **Plan de publicidad TikTok creado:**
   - Documento completo: `docs/marketing/tiktok_ads_plan.md`
   - Estrategia escalonada: €0 → €30-50 → €100-200 → €300-500/mes
   - ROI esperado: 4-11x
   - **Regla de negocio:** No invertir en publicidad hasta 10 clientes VIP de pago

6. **Repositorio organizado:**
   - Limpiados archivos huérfanos
   - Documentación reorganizada en `docs/`
   - `MANUAL_OPERATIVO.md` es ahora la única fuente de estado real

### Confirmado funcionando:
- ✅ Build pasa en Render
- ✅ `/start` responde en Telegram (probado con captura real)
- ✅ Webhook de Stripe creado y configurado
- ✅ Redis de Upstash conectado
- ✅ UptimeRobot monitoreando `/health` cada 5 min
- ✅ Repositorio actualizado en GitHub

---

## 🎯 Estado Actual del Proyecto

### ✅ COMPLETADO (Funcionando)

1. **Infraestructura**
   - [x] Bot desplegado en Render (Web Service, plan Free)
   - [x] Modo webhook implementado
   - [x] Auto-deploy desde GitHub
   - [x] UptimeRobot configurado
   - [x] Redis Upstash conectado

2. **Funcionalidades del Bot**
   - [x] `/start` - Registra usuario en BD
   - [x] `/help` - Guía de comandos
   - [x] `/status` - Estado del servicio
   - [x] `/premium` - Genera checkout de Stripe
   - [x] Webhook `/webhook/stripe` - Procesa pagos
   - [x] Generación de invitaciones automáticas al grupo VIP

3. **Pagos y Monetización**
   - [x] Stripe configurado
   - [x] Webhook activo
   - [x] Checkout funcional
   - [x] Variables de entorno en Render

4. **Documentación**
   - [x] Manual Operativo (este archivo)
   - [x] Guía de deploy (`docs/deployment/DEPLOY_NOW.md`)
   - [x] Estrategia de contenido (`docs/marketing/content_strategy.md`)
   - [x] Plan de publicidad TikTok (`docs/marketing/tiktok_ads_plan.md`)
   - [x] Plan de lanzamiento (`docs/launch/launch_plan.md`)

### ⚠️ PENDIENTE (Por hacer)

#### 🔴 CRÍTICO (Bloquea lanzamiento)

1. **Bot admin del grupo VIP** ⚠️
   - **Estado:** NO confirmado
   - **Acción requerida:** Ir a Telegram → Grupo VIP → Añadir @IdG_analisis_bot como admin con permiso "Invitar usuarios"
   - **Por qué es crítico:** Sin esto, el pago se procesa pero el usuario NO recibe invitación al grupo
   - **Cómo verificar:** Revisar logs de Render después de un pago de prueba

2. **Pago de prueba en Stripe** ⚠️
   - **Estado:** NO realizado
   - **Acción requerida:** 
     1. Activar modo TEST en Stripe
     2. Comprar plan VIP con tarjeta de prueba (4242 4242 4242 4242)
     3. Verificar flujo completo: pago → webhook → VIP activado → invitación enviada
   - **Por qué es crítico:** Sin esto, no sabes si el flujo funciona antes de tener clientes reales

3. **Base de datos persistente** ⚠️
   - **Estado:** NO implementado
   - **Problema:** SQLite se borra en cada redeploy en plan Free de Render
   - **Impacto:** Se pierden usuarios, VIPs, historial de pagos
   - **Opciones:**
     - **Opción A (Recomendada):** Upgrade a Render Starter ($7/mes) → Disco persistente de 1GB
     - **Opción B (Gratis):** Migrar a PostgreSQL en Supabase/Neon → Requiere cambios de código
   - **Decisión pendiente:** Esperando que usuario elija opción

#### 🟡 IMPORTANTE (Afecta funcionalidad)

4. **`/analisis` deshabilitado**
   - **Estado:** Desactivado (falta API key)
   - **Acción requerida:** Comprar créditos en console.anthropic.com ($10-20 iniciales)
   - **Regla de negocio:** No activar hasta tener 10+ clientes VIP pagando
   - **Cuándo:** Cuando haya ventas en cola

5. **Contenido 100% manual**
   - **Estado:** No automatizado
   - **Actual:** Usuario publica manualmente en canal Telegram
   - **Futuro:** Podría automatizarse, pero no es prioritario para lanzamiento

#### 🟢 MEJORA (No bloquea)

6. **Cancelación de suscripciones** - No probada con pagos reales
7. **Tests de integración** - Solo hay tests unitarios
8. **Monitoreo avanzado** - Faltan dashboards y alertas

---

## 🗂️ Qué aplicación se usa para cada cosa

| Servicio | Para qué | Dónde entrar | Estado |
|---|---|---|---|
| **GitHub** | Guarda código, auto-deploy en Render | github.com/cristobalsotoacosta03-dot/tipster-ai-bot | ✅ Activo |
| **Render.com** | Aloja bot 24/7 (plan Free, webhook) | dashboard.render.com → tipster-ia-bot | ✅ Activo |
| **BotFather** | Crea/admin bot (@IdG_analisis_bot) | Chat con @BotFather → `/mybots` | ✅ Configurado |
| **Anthropic Console** | API de Claude (para `/analisis`) | console.anthropic.com | ⚠️ Pendiente activar |
| **Stripe** | Cobra suscripciones VIP | dashboard.stripe.com | ✅ Configurado |
| **Upstash** | Redis cache (gratis) | console.upstash.com | ✅ Conectado |
| **UptimeRobot** | Mantiene bot despierto | dashboard.uptimerobot.com | ✅ Activo |
| **API-Football** | Datos de partidos | api-football.com | ✅ Configurado |
| **Telegram Grupo VIP** | Grupo de pago | @IdG_analisis_bot (grupo privado) | ⚠️ Pendiente: bot debe ser admin |

---

## 💰 Costes Actuales y Futuros

| Concepto | Estado Actual | Cuándo Pagar / Cuánto |
|---|---|---|
| **Hosting (Render)** | Gratis (Web Service Free) | $7/mes (Starter) si necesitas disco persistente o eliminar "arranque en frío" |
| **Telegram Bot API** | Gratis siempre | Nunca cuesta |
| **Claude API (Anthropic)** | ⚠️ Desactivada (placeholder) | De pago por uso. Activar cuando tengas 10+ VIPs. $10-20 crédito inicial suficientes |
| **Stripe** | Gratis crear cuenta | Comisión 1.4% + 0.25€ por cobro (se descuenta automáticamente) |
| **Upstash Redis** | Gratis (tier free) | Solo si superas límite free tier |
| **API-Football** | Gratis (100 req/día) | Planes de pago si necesitas >100 consultas/día |
| **UptimeRobot** | Gratis (1 monitor) | Solo si quieres más monitores o intervalos más cortos |
| **Publicidad TikTok** | €0 (orgánico) | No invertir hasta 10 clientes VIP. Luego: €30-50/semana (Semana 2), €100-200 (Semana 3-4) |

**Resumen de costes actuales: €0/mes**  
**Costes cuando lances:** €0-50/mes (publicidad) + €7/mes (si upgrade Render) + comisiones Stripe

---

## ⚠️ Limitaciones Conocidas

1. **Tiempo de respuesta tras inactividad (30-60s)**
   - UptimeRobot hace ping cada 5 min para evitar sleep
   - No 100% garantizado que nunca haya "arranque en frío"
   - **Solución definitiva:** Upgrade a Render Starter ($7/mes)

2. **Base de datos NO persistente en plan Free**
   - SQLite se borra en cada redeploy
   - **Impacto:** Se pierden usuarios, VIPs, pagos
   - **Solución:** Opción A ($7/mes disco) u Opción B (Postgres gratis)
   - **Cuándo resolver:** Antes de tener clientes de pago reales

3. **`/analisis` deshabilitado**
   - Falta `ANTHROPIC_API_KEY` real
   - Muestra "disponible muy pronto"
   - **Cuándo activar:** Cuando tengas 10+ clientes VIP y quieras invertir en Claude

4. **Bot debe ser admin del grupo VIP**
   - Sin permiso "Invitar usuarios", no puede generar invitaciones
   - **Acción:** Configurar YA antes de lanzar

5. **Contenido 100% manual**
   - No hay publicación automática en canal
   - Usuario publica manualmente desde Telegram
   - **Futuro:** Podría automatizarse, no prioritario

6. **Cancelación de suscripciones no probada**
   - Código está implementado pero no probado con pago real
   - **Riesgo:** Bajo, pero hay que verificar

---

## 📋 Checklist de Lanzamiento

### ✅ Completado
- [x] Bot desplegado en Render (webhook, plan Free)
- [x] `/start`, `/help`, `/status` funcionando
- [x] `/premium` genera checkout real de Stripe
- [x] Webhook de Stripe configurado (`/webhook/stripe`)
- [x] UptimeRobot monitoreando `/health`
- [x] Redis Upstash conectado
- [x] API-Football configurada
- [x] Repositorio actualizado en GitHub
- [x] Plan de publicidad TikTok creado
- [x] Documentación completa

### 🔴 Pendiente CRÍTICO (Hacer antes de lanzar)
- [ ] **Bot es admin del grupo VIP** (con permiso de invitar)
- [ ] **Pago de prueba en Stripe** (validar flujo completo)
- [ ] **Decidir: Opción A ($7/mes) u Opción B (Postgres gratis)** para BD persistente

### 🟡 Pendiente IMPORTANTE (Hacer esta semana)
- [ ] Configurar canal Telegram de captación (@TipsterIA_Gratis)
- [ ] Grabar 4-5 videos para TikTok
- [ ] Diseñar lead magnet (PDF "5 Errores")
- [ ] Crear mensaje de bienvenida del canal
- [ ] Compartir en grupos de apuestas

### 🟢 Futuro (Mes 1-2)
- [ ] Activar `/analisis` con Claude API (cuando tengas 10+ VIPs)
- [ ] Migrar a PostgreSQL (cuando tengas ingresos)
- [ ] Implementar publicación automática de picks
- [ ] Añadir tests de integración
- [ ] Mejorar monitoreo (dashboards, alertas)

---

## 🎯 Próximos Pasos Inmediatos (Orden de Prioridad)

### HOY - 16/07/2026 (Tarde)

**1. Hacer bot admin del grupo VIP (30 min)**
```
Pasos:
1. Ir a Telegram → Grupo VIP
2. Click en nombre del grupo → "Administradores"
3. "Añadir administrador" → Buscar @IdG_analisis_bot
4. Dar permisos: ✅ "Invitar usuarios" ✅ "Mensajes"
5. Guardar
6. Verificar en Render → Logs que no hay errores de permisos
```

**2. Hacer pago de prueba en Stripe (15 min)**
```
Pasos:
1. Ir a dashboard.stripe.com
2. Activar modo TEST (toggle superior derecho)
3. Ir a "Productos" → Crear producto de prueba (€29.99)
4. Ir a "Webhooks" → Verificar que el endpoint está activo
5. Hacer checkout de prueba:
   - Usar tarjeta: 4242 4242 4242 4242
   - Fecha: cualquier fecha futura
   - CVC: cualquier 3 dígitos
6. Completar pago
7. Verificar en Render → Logs:
   - Webhook se dispara
   - Usuario se marca como VIP
   - Se genera invitación
8. Verificar que usuario recibe link de invitación en Telegram
```

**3. Verificar flujo completo (10 min)**
```
Checklist:
- [ ] Pago se procesa en Stripe
- [ ] Webhook llega a Render
- [ ] Usuario se marca como VIP en BD
- [ ] Se genera link de invitación
- [ ] Usuario recibe link en Telegram
- [ ] Usuario puede unirse al grupo VIP
- [ ] Bot reconoce al usuario como VIP en `/status`
```

### MAÑANA - 17/07/2026

**4. Decidir estrategia de base de datos (30 min)**
```
Opción A (Recomendada - Rápida):
- Upgrade a Render Starter ($7/mes)
- Configurar disco persistente 1GB
- Ventaja: Sin cambios de código, 5 minutos
- Desventaja: Coste $7/mes

Opción B (Gratis - Más trabajo):
- Migrar a PostgreSQL en Supabase/Neon
- Modificar código (cambiar SQLite por SQLAlchemy)
- Ventaja: Gratis, más escalable
- Desventaja: 2-3 horas de trabajo

Mi recomendación: Opción A por velocidad. Cuando tengas ingresos, migrar a Opción B.
```

**5. Si eliges Opción A: Configurar disco en Render (10 min)**
```
Pasos:
1. Ir a dashboard.render.com → tipster-ia-bot
2. "Disks" → "Add Disk"
3. Name: tipster-data
4. Mount Path: /opt/render/project/src/data
5. Size: 1 GB
6. Save
7. Render hará redeploy automático
```

**6. Si eliges Opción B: Empezar migración a PostgreSQL (2-3h)**
```
Pasos:
1. Crear cuenta en supabase.com (gratis)
2. Crear proyecto PostgreSQL
3. Obtener connection string
4. Modificar código:
   - Cambiar sqlite3 por SQLAlchemy
   - Actualizar database.py
   - Probar localmente
5. Actualizar variables de entorno en Render
6. Deploy y probar
```

**7. Grabar 2-3 videos para TikTok (2-3h)**
```
Videos a grabar (ver plan en docs/marketing/tiktok_ads_plan.md):
1. "El Error #1 de los Apostadores" (45s)
2. "Este Partido Tiene VALUE" (50s)
3. "Cómo Ganar Apostando" (60s)

Herramientas:
- CapCut (edición)
- Canva (gráficos)
- Móvil para grabar

Tips:
- Hook en primeros 3 segundos
- Texto en pantalla (muchos ven sin sonido)
- CTA claro: "Link en bio"
```

### FIN DE SEMANA - 18/07/2026 (Lanzamiento)

**8. Lanzamiento oficial**
```
Viernes 16/07 (Hoy):
- [ ] 18:00 - Publicar primer video TikTok
- [ ] 19:00 - Activar bot en producción
- [ ] 20:00 - Primer análisis en vivo Telegram

Sábado 17/07:
- [ ] 10:00 - Video 2 + tips en canal
- [ ] 15:00 - Compartir en grupos de apuestas
- [ ] 19:00 - Análisis en vivo

Domingo 18/07:
- [ ] 10:00 - Resumen resultados fin de semana
- [ ] 15:00 - Oferta especial lanzamiento
- [ ] 19:00 - Cierre y estadísticas
```

---

## 📊 Métricas a Monitorear (Dashboard Diario)

### Métricas de Video (TikTok)
- Visualizaciones por video
- Engagement rate (likes + comments + shares / views)
- Tasa de finalización
- Clics en bio
- Compartidos

**Objetivos:**
- Video 1: 100+ views, 5% engagement
- Video 2: 500+ views, 8% engagement
- Video 3: 1,000+ views, 10% engagement

### Métricas de Canal Telegram
- Nuevos miembros por día
- Tasa de retención
- Clics en enlaces
- Reportes de spam

**Objetivos:**
- Día 1: 50 miembros
- Día 2: 200 miembros
- Día 3: 500 miembros

### Métricas de Bot
- Usuarios únicos
- Análisis solicitados
- Tasa de conversión a VIP
- Tiempo de respuesta

**Objetivos:**
- Día 1: 10 usuarios, 10 análisis
- Día 2: 30 usuarios, 30 análisis
- Día 3: 50 usuarios, 50 análisis

### Métricas de Conversión
- Clics en bio
- Registros en Telegram
- Checkouts iniciados
- Pagos completados
- Ingresos generados

**Objetivos:**
- Día 1: 0-2 clientes VIP
- Día 2: 5-10 clientes VIP
- Día 3: 10-20 clientes VIP
- MRR inicial: €300-600

---

## 🚨 Plan de Contingencia

### Si el bot falla
1. **Diagnóstico rápido (5 min):** Revisar logs en Render
2. **Solución temporal (15 min):** Modo mantenimiento, ofrecer descuento compensatorio
3. **Solución permanente (1-2h):** Fix + deploy hotfix

### Si no hay tráfico
1. Ampliar distribución (más grupos, influencers)
2. Mejorar hooks (A/B testing)
3. Ajustar CTA

### Si no hay conversiones
1. Revisar pricing (¿€29.99 es muy caro?)
2. Mejorar pitch de venta
3. Aumentar valor percibido
4. Ofrecer descuento de lanzamiento (20-30%)

### Si el CPA es muy alto (>€20)
1. Restringir segmentación
2. Mejorar targeting
3. Mejorar creatividades
4. Optimizar CTA

---

## 📈 Proyecciones Financieras

### Mes 1: Lanzamiento
- **Inversión:** €130-230 (publicidad €80-130 + APIs €50-100)
- **Ingresos:** 50 VIPs × €29.99 = €1,499
- **ROI:** 6-11x

### Mes 2: Crecimiento
- **Inversión:** €400-670 (publicidad €300-500 + APIs €100-150)
- **Ingresos:** 120 VIPs × €29.99 = €3,598
- **ROI:** 5-9x

### Mes 3: Escalamiento
- **Inversión:** €820-1,350 (publicidad €600-1,000 + APIs €200-300)
- **Ingresos:** 200 VIPs × €29.99 = €5,998
- **ROI:** 4-7x

---

## 🎓 Reglas de Negocio (No olvidar)

1. **No invertir en publicidad hasta 10 clientes VIP** (regla definida)
2. **No activar Claude API hasta tener ventas en cola** (decisión tomada)
3. **Resolver BD persistente antes de escalar** (crítico)
4. **Validar flujo de pago completo antes de lanzar** (crítico)
5. **Monitorear métricas diariamente** durante lanzamiento

---

## 📞 Contactos y Recursos

### Servicios
- **GitHub:** https://github.com/cristobalsotoacosta03-dot/tipster-ai-bot
- **Render:** https://dashboard.render.com → tipster-ia-bot
- **Stripe:** https://dashboard.stripe.com
- **Anthropic:** https://console.anthropic.com
- **Upstash:** https://console.upstash.com
- **UptimeRobot:** https://dashboard.uptimerobot.com
- **API-Football:** https://www.api-football.com

### Documentación del Proyecto
- `README.md` - Información general del proyecto
- `MANUAL_OPERATIVO.md` - Este archivo (estado real)
- `docs/deployment/DEPLOY_NOW.md` - Guía de deployment
- `docs/marketing/content_strategy.md` - Estrategia de contenido
- `docs/marketing/tiktok_ads_plan.md` - Plan de publicidad TikTok
- `docs/launch/launch_plan.md` - Plan de lanzamiento

---

## ✅ Checklist Rápido (Para próxima sesión)

Antes de empezar a trabajar, verificar:

- [ ] Bot está corriendo en Render (ver logs)
- [ ] UptimeRobot está activo (ver dashboard)
- [ ] Stripe está configurado (ver webhook)
- [ ] Redis Upstash está conectado
- [ ] GitHub tiene los últimos cambios

Si algo falla, revisar `MANUAL_OPERATIVO.md` sección "Limitaciones Conocidas".

---

**Preparado por:** Tech Lead / Product Manager  
**Última actualización:** 16/07/2026 - 12:42  
**Próxima actualización:** 17/07/2026 (Post-lanzamiento)

**Nota para Claude:** Este archivo es la fuente de verdad del estado del proyecto. Actualízalo cada vez que haya cambios importantes.