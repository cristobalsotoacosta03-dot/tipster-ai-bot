# Mensaje de bienvenida del canal gratis (listo para publicar)

**Estado:** borrador para tu revisión — nada de esto se ha publicado. No se ha
tocado ningún canal de Telegram real ni se ha gastado nada en difusión.

**Por qué este archivo y no solo el de `content_strategy.md`:** ese documento
ya tenía un borrador de bienvenida, pero:
1. Usa un handle de VIP estático (`@TipsterIA_VIP`) que no existe en el
   producto real — el acceso VIP se concede con un enlace de invitación de
   un solo uso generado automáticamente tras el pago (ver
   `_create_vip_invite_link` en `src/bot/telegram_bot.py`), no uniéndose a un
   canal público. Un mensaje que prometa lo primero confundiría al usuario.
2. Cifras como "68% de acierto" no existen todavía — el bot no tiene
   histórico real de aciertos. Publicar una cifra de acierto inventada en
   contenido dirigido a apuestas es el tipo de afirmación que puede
   considerarse publicidad engañosa. Este borrador no incluye ninguna cifra
   que no puedas respaldar hoy.

Sustituye `@TuBotReal` y `@TuCanalReal` por los handles reales antes de
publicar.

---

```
👋 Bienvenido a Tipster IA

Análisis de fútbol con IA (Claude) para apostar con datos, no con intuición.

📊 Aquí encontrarás:
• Picks gratuitos con el análisis detrás (no solo "apuesta a X")
• Estadísticas reales por partido: forma reciente, descanso, historial h2h
• Contenido educativo sobre value betting y gestión de bankroll

🎯 Cómo funciona:
1. Habla con el bot: @TuBotReal
2. Escribe /analisis [equipo1] vs [equipo2]
3. Recibe un análisis táctico con datos reales (no inventados) en segundos

💎 ¿Quieres más?
El plan VIP (€29.99/mes o €299/año) da análisis premium ilimitados,
pronóstico con stake recomendado y acceso a un grupo VIP privado.
Escribe /premium al bot para ver los detalles y suscribirte.

⚠️ Apostar conlleva riesgo. Nunca apuestes más de lo que puedas permitirte
perder. Este canal es informativo, no es asesoramiento financiero.

🤖 Bot: @TuBotReal
📢 Este canal: @TuCanalReal
```

---

## Nota para fijar (pin) en el canal

Versión corta, para fijar como mensaje permanente:

```
📌 Empieza aquí: habla con @TuBotReal y escribe /analisis [equipo1] vs [equipo2]
para tu primer análisis gratis. /premium para VIP. Apostar conlleva riesgo —
apuesta responsable.
```
