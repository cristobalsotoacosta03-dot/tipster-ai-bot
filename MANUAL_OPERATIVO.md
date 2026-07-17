# Manual Operativo - Tipster IA Bot

**Última actualización:** 17/07/2026  
**Fuente de verdad del estado del proyecto** — actualizar en cada sesión relevante.

---

## Dónde estamos ahora (17/07/2026)

Bot de Telegram (`@IdG_analisis_bot`) de análisis de apuestas deportivas, con canal gratis + grupo VIP de pago vía Stripe. Desplegado en Render (Web Service Free, webhook) desde GitHub `cristobalsotoacosta03-dot/tipster-ai-bot`, rama `main`, auto-deploy.

### Estado del servicio (confirmado)

| Componente | Estado |
|---|---|
| Sistema | Operativo |
| Bot Telegram | En línea |
| Claude AI | Conectado (API key configurada; `/analisis` aún no liberado al usuario) |
| API de Datos (API-Football) | Configurada |
| Stripe | Configurado |
| Redis Upstash | Conectado |
| UptimeRobot | Activo (`/health` cada 5 min) |
| Canal gratis + Grupo VIP | Creados; bot es admin del VIP |

### Lo que funciona hoy

- `/start` — registra usuario en BD
- `/help` — guía de comandos
- `/status` — estado del servicio
- `/premium` — checkout real de Stripe
- Webhook `/webhook/stripe` — activa VIP + invitación de un solo uso al grupo
- Build y deploy en Render OK
- Dos canales de Telegram creados (captación + VIP)

### Lo que falta (prioridad)

1. **`/analisis`** — apartado de análisis aún no operativo de cara al usuario (siguiente bloque de trabajo técnico).
2. **Pago de prueba Stripe** — validar flujo completo en modo TEST (tarjeta `4242…`) antes de clientes reales.
3. **BD persistente** — SQLite se borra en cada redeploy del plan Free. Elegir:
   - **A (rápida):** Render Starter $7/mes + disco 1GB
   - **B (gratis):** PostgreSQL en Supabase/Neon (más código)
4. Contenido y captación (manual por ahora; no bloquea el producto técnico).

### Sesión 17/07/2026 — Datos reales para `/analisis` (partidos previos, forma, h2h)

Se pidió enriquecer el bot con "partidos previos de los equipos" al estilo BeSoccer/Sofascore para mejores pronósticos. Ninguno de los dos tiene API pública (Sofascore es scraping no oficial contra sus ToS; BeSoccer no tiene API), así que se optó por explotar mejor la fuente ya integrada y gratuita: **API-Football, plan free (100 req/día)**.

Cambios de código:
- `src/data/stats_fetcher.py` reescrito: se eliminó el bug de `league_id=39` (Premier League) y `season=2024` fijos — ahora se resuelve la liga y temporada real de cada equipo (`resolve_league_context`). Se añadieron fixtures reales recientes (`get_recent_fixtures`) para derivar forma (W/D/L), goles a favor/en contra y días de descanso reales. El head-to-head ahora también es estructurado (no solo texto), con % de BTTS y Over 2.5 reales calculados sobre los mismos partidos.
- Se **eliminaron** las métricas que nunca fueron reales (xG, xGA, PPDA, posesión, métricas físicas, set pieces, formación, árbitro, clima, motivación): antes eran `dict.get(key, valor_inventado)` que siempre devolvían el valor fabricado y se presentaban a Claude/usuario como datos reales.
- `src/analyzer/prompt_engine.py` reescrito para consumir solo datos reales; cuando falta un dato, el prompt dice "No disponible" en vez de inventar una cifra. De paso se corrigió un bug donde el prompt **premium (VIP, la parte de pago)** nunca recibía sus placeholders reales y mandaba a Claude texto con `$strategic_context` etc. literalmente sin sustituir.
- `src/analyzer/match_analyzer.py`: arreglado el hack de timestamp (`logging.Formatter().formatTime(...)` → `datetime.now().isoformat()`).
- Nueva interfaz `src/data/providers/base.py` (`MatchDataProvider` Protocol) para poder añadir en el futuro una segunda fuente gratuita y legítima (football-data.org, TheSportsDB) sin rehacer el pipeline. No se implementó ninguna fuente nueva esta sesión, solo la interfaz.
- Tests nuevos: `tests/test_stats_fetcher.py`, `tests/test_match_analyzer.py`; `tests/test_prompt_engine.py` reescrito. `pytest` en verde salvo un fallo preexistente y no relacionado en `tests/test_database.py::test_get_user_analyses` (bug ya presente antes de esta sesión, no tocado).

Presupuesto de cuota: un análisis completo pasa de ~7 a ~11 llamadas a API-Football (con el nuevo fixtures/liga por equipo). Con caché (24h equipo/liga, 6h análisis completo vía `cache_manager.py`) se mantiene dentro del límite gratuito para uso moderado; si el volumen crece, hay que revisar el límite de 100 req/día.

### Sesión 17/07/2026 (continuación) — Fuentes gratuitas adicionales (fallback)

Se añadieron dos proveedores gratuitos más, usados **solo como fallback** cuando API-Football no encuentra alguno de los dos equipos (agotado el cupo de 100 req/día, o equipo fuera de su cobertura):

- **`src/data/providers/football_data_org.py`** — football-data.org, tier gratuito real (cuenta personal gratis, sin coste). Cubre ~12 competiciones top (Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Champions League, etc.). Sin endpoint de búsqueda por nombre en el plan free, así que busca el equipo recorriendo la plantilla de cada competición (cacheado 24h).
- **`src/data/providers/thesportsdb.py`** — TheSportsDB, tier gratuito real (cuenta personal gratis, sin coste). Solo da acceso a los últimos 5 partidos por equipo, así que su cobertura de forma/h2h es más limitada — es un fallback, no un sustituto de API-Football.
- Ambos requieren que **tú** te registres gratis y pongas la clave en `.env` (`FOOTBALL_DATA_ORG_KEY`, `THESPORTSDB_API_KEY`). Si no se configuran, no hacen nada — cero cambio de comportamiento.
- `src/data/providers/base.py` ganó una función compartida `build_match_data()` para que los tres proveedores (API-Football + los 2 nuevos) generen el mismo formato de datos hacia `prompt_engine.py`, sin duplicar código.
- `match_analyzer.py`: nuevo método `_fetch_match_data()` que prueba API-Football primero y solo si falla intenta los fallbacks configurados, en orden.
- Ninguno de los dos fallbacks da datos de lesiones (no existen en sus planes gratuitos) — se devuelve lista vacía, honesto, nunca inventado.
- Tests nuevos: `tests/test_football_data_org.py`, `tests/test_thesportsdb.py`, y casos de fallback en `tests/test_match_analyzer.py`. Todo en verde salvo el mismo fallo preexistente y no relacionado en `test_database.py`.

**Nota:** no se usó BeSoccer ni Sofascore — ninguno tiene API pública gratuita legítima (ver decisión de la sesión anterior).

### Sesión 17/07/2026 (continuación 2) — Cuotas de mercado reales (The Odds API)

Investigación externa (Gemini Deep Research) sobre más fuentes de datos deportivos. La mayoría de lo que propuso (TheStatsAPI, PropLine, iSports API, Statorium) tiene fuentes de verificación dudosas (marketing propio, directorios tipo listicle) — **no se integró nada de eso sin verificar antes**. Se confirmó de forma independiente (contrastando su documentación real) que **The Odds API** sí es fiable y con free tier real: 500 peticiones/mes, sin tarjeta.

- **`src/data/odds_provider.py`** (nuevo) — `OddsProvider`, obtiene cuotas reales de casas de apuestas para ~6 ligas top europeas (una llamada por liga cubre todos sus partidos, cacheado 45 min). No forma parte del `MatchDataProvider` (es cuotas, no resultados); es un enriquecimiento opcional del pipeline.
- `match_analyzer.py`: si `ODDS_API_KEY` está configurada, tras obtener `match_data` intenta añadir `market_odds` (cuotas medias reales + probabilidad implícita) — **best-effort, nunca bloquea el análisis** si falla o no encuentra el partido.
- `prompt_engine.py`: nueva sección "Mercado de Cuotas" en los tres templates (full/express/premium), con cuotas reales cuando existen o "No disponible" si no. Se le pide a Claude que compare su propia estimación con la probabilidad implícita del mercado (sin quitar el margen de la casa — se avisa de que es probabilidad implícita bruta, no "verdadera").
- Requiere que **tú** te registres gratis en the-odds-api.com y pongas `ODDS_API_KEY` en `.env`. Si no se configura, no cambia nada.
- Tests nuevos: `tests/test_odds_provider.py` + casos de enriquecimiento en `tests/test_match_analyzer.py` + casos en `tests/test_prompt_engine.py`. Todo en verde salvo el mismo fallo preexistente en `test_database.py`.

### Sesión 17/07/2026 (continuación 3) — Fix crítico de API-Football + inicio de "consenso de tipsters"

**Bug crítico encontrado y corregido**: `/analisis` fallaba en producción con "No pude encontrar datos" para CUALQUIER equipo (probado con Real Madrid vs Barcelona, España vs Argentina). Causa: `stats_fetcher.py` llamaba a API-Football vía **RapidAPI** (host `api-football-v1.p.rapidapi.com`), pero la clave real (`API_FOOTBALL_KEY` en Render) es de la cuenta **directa de API-Sports** (`dashboard.api-football.com`) — son dos sistemas de auth distintos. Verificado con curl real: RapidAPI devolvía 403, el host directo (`v3.football.api-sports.io` con header `x-apisports-key`) devuelve 200 con la cuenta real (plan Free, 100 req/día, activo hasta 2027-07-16). **Corregido y desplegado** (commit `eed1d0c`, push ya hecho, Render redeployando). Pendiente de confirmar por el usuario que `/analisis` ya funciona tras el redeploy.

**Nueva iniciativa en marcha (NO completada)**: detección de "consenso entre tipsters" — leer canales públicos de Telegram de tipsters de confianza (que el usuario elija) y usarlo como señal agregada más para el prompt de Claude (ej. "4 de 6 tipsters monitorizados favorecen a X"), nunca republicando contenido literal ni atribuyendo a un tipster concreto (decisión explícita del usuario para evitar problemas de propiedad de contenido).

Motivo técnico: el Bot API de Telegram (`TELEGRAM_BOT_TOKEN`) NO puede leer canales ajenos a los que no le añadan como admin. Hace falta la API de cliente (Telethon), que actúa como una cuenta de usuario real leyendo contenido público — como seguir el canal a mano, pero automatizado. Esto es legítimo para canales públicos (no es scraping de un sitio que lo prohíba, es contenido diseñado para difusión pública), a diferencia de TikTok (sin API, ToS lo prohíbe expresamente, descartado).

Estado exacto a fecha de hoy:
- Usuario creó cuenta de aplicación en my.telegram.org con su **número de trabajo** (decisión consciente, sabiendo que liga esa cuenta de Telegram a ese número).
- `api_id = 36881932` (confirmado, sin ambigüedad).
- `api_hash` pendiente de confirmar como texto plano (se dio por captura de pantalla, con riesgo de ambigüedad "l" vs "1" — **no usar el de la captura sin que el usuario lo confirme por texto**).
- Creado `scripts/telegram_consensus_login.py` (login interactivo, debe ejecutarlo el usuario en su propia máquina — el código de verificación le llega a él, no se puede automatizar desde aquí). Genera una `TELEGRAM_CONSENSUS_SESSION` (string) que luego va al `.env`.
- Añadido `telethon==1.34.0` a `requirements.txt`, y placeholders en `config/settings.py`/`.env.example` (`TELEGRAM_CONSENSUS_API_ID`, `TELEGRAM_CONSENSUS_API_HASH`, `TELEGRAM_CONSENSUS_SESSION`) — todavía sin lógica de lectura de canales ni de detección de consenso (eso es el siguiente paso, pendiente de que el usuario haga el login y dé la lista de canales de tipsters de confianza).
- El usuario va a continuar este trabajo desde su **portátil** (dejará este ordenador aparcado una temporada). Repo ya empujado a GitHub (`eed1d0c`) para que el portátil pueda clonar/hacer pull. El `.env` NO se sube a git — el usuario debe copiarlo a mano o reconstruirlo desde Render + sus propios registros.

**Próximo paso literal**: confirmar `api_hash` por texto → usuario ejecuta `scripts/telegram_consensus_login.py` (en el portátil o donde esté) → pega la sesión resultante en `.env` → dar la lista de canales de tipsters de confianza → diseñar la lógica de detección de consenso (heurística por palabras clave, no NLP completo).

### Reglas de negocio vigentes

1. No invertir en publicidad hasta **10 clientes VIP de pago**.
2. No gastar en Claude a escala hasta tener ventas VIP en cola (créditos mínimos solo si hace falta probar `/analisis`).
3. Resolver BD persistente **antes** de escalar con clientes reales.
4. Validar flujo de pago completo antes de lanzar captación seria.

---

## Servicios (mapa rápido)

| Servicio | Para qué | Dónde | Estado |
|---|---|---|---|
| GitHub | Código + auto-deploy | github.com/cristobalsotoacosta03-dot/tipster-ai-bot | Activo |
| Render.com | Hosting 24/7 (Free, webhook) | dashboard.render.com → tipster-ia-bot | Activo |
| BotFather | Bot `@IdG_analisis_bot` | Telegram | Configurado |
| Anthropic | Claude (análisis) | console.anthropic.com | Conectado; uso controlado |
| Stripe | Suscripciones VIP | dashboard.stripe.com | Configurado |
| Upstash | Redis cache | console.upstash.com | Conectado |
| UptimeRobot | Keep-alive `/health` | dashboard.uptimerobot.com | Activo |
| API-Football | Datos de partidos | api-football.com | Configurado |
| Telegram VIP | Grupo de pago | privado, bot admin | Creado |
| Telegram gratis | Canal captación | — | Creado |

---

## Costes

| Concepto | Ahora | Cuándo / cuánto |
|---|---|---|
| Render | €0 (Free) | $7/mes si Starter + disco |
| Telegram | €0 | Nunca |
| Claude | Conectado, uso mínimo | Por uso; activar a escala con 10+ VIP |
| Stripe | €0 cuenta | 1.4% + 0.25€ por cobro |
| Upstash | Free tier | Si se supera free |
| API-Football | Free (100 req/día) | Plan de pago si hace falta |
| UptimeRobot | Free (1 monitor) | — |
| Publicidad | €0 | Solo tras 10 VIP |

**Coste actual: ~€0/mes.**

---

## Limitaciones conocidas

1. **Arranque en frío** (30–60s tras inactividad) en plan Free; UptimeRobot mitiga, no elimina.
2. **SQLite no persistente** en Free → se pierden usuarios/VIP en redeploy.
3. **`/analisis`** pendiente de cerrar y liberar al usuario.
4. **Contenido manual** en canal (sin publicación automática).
5. **Cancelación de suscripciones** implementada, no probada con pago real.

---

## Checklist

### Hecho
- [x] Bot en Render (webhook, Free)
- [x] `/start`, `/help`, `/status`
- [x] `/premium` + webhook Stripe
- [x] UptimeRobot + Redis + API-Football
- [x] Repo en GitHub, auto-deploy
- [x] Bot admin del grupo VIP
- [x] Canal gratis + grupo VIP creados
- [x] Documentación reorganizada (17/07/2026)

### Crítico (antes de clientes reales)
- [ ] Pago de prueba Stripe (flujo completo)
- [ ] Decidir y aplicar BD persistente (A o B)

### Producto
- [ ] Cerrar y liberar `/analisis`
- [ ] Probar cancelación de suscripción con pago real

### Captación (cuando el producto esté listo)
- [ ] Mensaje de bienvenida del canal gratis
- [ ] Primeros contenidos / videos
- [ ] Lead magnet (opcional)

### Futuro
- [ ] Publicación automática de picks
- [ ] Tests de integración
- [ ] Monitoreo avanzado

---

## Siguiente paso técnico recomendado

1. **Cerrar `/analisis`** (flujo datos → Claude → formato → límites free/VIP).
2. **Pago de prueba Stripe** en modo TEST y verificar logs en Render + invitación VIP.
3. **BD persistente** (preferible A si se quiere velocidad; B si se quiere €0).

---

## Documentación del repo

| Archivo | Uso |
|---|---|
| `README.md` | Visión general + quickstart desarrollo |
| `MANUAL_OPERATIVO.md` | **Este archivo** — estado real |
| `PRINCIPIOS_IA.md` | Qué hace / no hace la IA |
| `docs/README.md` | Índice de docs |
| `docs/deployment/DEPLOY_NOW.md` | Runbook deploy Render |
| `docs/technical/api_documentation.md` | Arquitectura técnica |
| `docs/technical/prompts_documentation.md` | Diseño de prompts |
| `docs/marketing/content_strategy.md` | Estrategia de contenido |
| `docs/marketing/tiktok_ads_plan.md` | Plan ads (solo tras 10 VIP) |

---

## Contingencia rápida

- **Bot caído:** logs en Render → fix → redeploy.
- **Sin tráfico:** más distribución orgánica; no ads hasta 10 VIP.
- **Sin conversión:** revisar pitch/precio; no gastar en ads.
- **CPA alto:** no aplica hasta fase de ads.

---

**Nota:** Actualizar este archivo en cada sesión con cambios de estado reales. No mezclar proyecciones con hechos.
