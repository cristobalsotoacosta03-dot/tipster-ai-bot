# Índice de documentación

Guía de qué documento mirar según lo que necesites.

## Para saber el estado real del proyecto ahora mismo

👉 **[`MANUAL_OPERATIVO.md`](../MANUAL_OPERATIVO.md)** (raíz del repo). Es el único documento que se mantiene actualizado sesión a sesión: qué servicio hace qué, qué falta por hacer, y qué se hizo en la última sesión. Empieza siempre por ahí.

## Documentación técnica (`technical/`)

Referencia de arquitectura y funcionamiento interno, no cambia con cada sesión:
- [`api_documentation.md`](technical/api_documentation.md) — arquitectura técnica del sistema
- [`prompts_documentation.md`](technical/prompts_documentation.md) — diseño de los prompts de Claude
- [`deployment_guide.md`](technical/deployment_guide.md) — guía general de deployment

## Deployment (`deployment/`)

- [`DEPLOY_NOW.md`](deployment/DEPLOY_NOW.md) — runbook paso a paso para desplegar en Render desde cero (plan gratuito). El bot ya está desplegado; esto sirve como referencia para redeploys completos o para levantar una segunda instancia/entorno.

## Marketing (`marketing/`) — de cara a lo que viene

Playbook activo para cuando arranque la fase de captación:
- [`content_strategy.md`](marketing/content_strategy.md) — estrategia de contenido orgánico
- [`tiktok_ads_plan.md`](marketing/tiktok_ads_plan.md) — plan de publicidad TikTok. **Regla vigente: no se invierte en publicidad hasta 10 clientes VIP de pago**, sin importar cuánto tarde la fase orgánica.

## Archivo histórico (`archive/`)

Documentos del sprint inicial de 7 días (planificación y logs diarios). Útiles como contexto de cómo se construyó el proyecto, **no como fuente de estado actual**:
- [`sprint_plan.md`](archive/sprint_plan.md), [`launch_plan.md`](archive/launch_plan.md)
- `daily_logs/day_01` a `day_07` — ⚠️ `day_07_summary.md` incluye una sección de "resultados de lanzamiento" que es una simulación/proyección, no datos reales; tiene un aviso al principio del archivo.

## Otros documentos en la raíz

- [`README.md`](../README.md) — visión general del proyecto y quickstart de desarrollo
- [`PRINCIPIOS_IA.md`](../PRINCIPIOS_IA.md) — qué hace y qué no hace la IA en este sistema (política, útil también de cara a suscriptores)
