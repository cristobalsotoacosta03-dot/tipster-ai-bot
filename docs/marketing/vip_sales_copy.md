# Copy de venta VIP (listo para usar)

**Estado:** borrador para tu revisión. No se ha modificado ningún mensaje en
producción — el bot sigue usando los textos actuales de
`src/bot/telegram_bot.py` y `src/monetization/access_control.py` tal cual
estaban. Nada aquí se ha "activado".

Al igual que en los otros dos archivos de esta carpeta: no se incluyen
cifras de acierto ni testimonios, porque no hay datos reales todavía que
los respalden. En cuanto tengas resultados reales, hay un hueco marcado
más abajo para añadirlos.

---

## 1. Mensaje in-bot al alcanzar el límite gratuito

El bot ya tiene este mensaje implementado (`telegram_bot.py`, dentro de
`analisis_command`):

```
🚫 Límite diario alcanzado

Has usado tus {N} análisis gratuitos de hoy.
Usa /premium para acceso VIP ilimitado, o vuelve mañana.
```

Funciona bien porque es corto y aparece justo en el momento de fricción
(justo cuando el usuario quiere un análisis más). Sugerencia opcional para
subir la conversión sin tocar código ahora mismo — variante A/B a probar
manualmente cuando quieras, cambiando solo el texto:

```
🚫 Ya usaste tus {N} análisis gratis de hoy

Con VIP no hay límite diario, y los análisis son más completos
(incluyen stake recomendado). /premium para ver precios.
```

## 2. Pitch corto (para pinned message, bio, o respuesta rápida)

```
🎯 Tipster IA VIP: análisis táctico ilimitado + pronóstico con stake
recomendado, por 29,99€/mes. Sin permanencia. /premium en el bot.
```

## 3. Pitch largo (ya cubierto, con matices)

`content_strategy.md` ya tiene un pitch largo completo en su sección
"Material de Venta VIP" (título, propuesta de valor, objeciones y
respuestas) — no lo duplico aquí. Dos ajustes que sí conviene aplicar
cuando lo uses:

- **Quitar toda mención a "68% de acierto"** en el pitch y en las
  respuestas a objeciones ("nuestros miembros tienen un 68% de acierto vs
  52% promedio") — no hay datos que respalden esa cifra todavía.
- **Los testimonios de esa sección son ejemplos de estructura, no
  contenido real** — están firmados con nombres y ciudades ficticios
  ("Carlos M., Madrid", etc.). No publicar tal cual: o se sustituyen por
  testimonios reales de clientes reales (con su permiso explícito), o se
  quita la sección hasta tener alguno.

## 4. Descripción para el checkout de Stripe (opcional, requiere un cambio de código menor)

`payment_handler.py::create_checkout_session` no pasa actualmente ninguna
descripción de producto a `stripe.checkout.Session.create` — Stripe muestra
solo el nombre del Price configurado en el dashboard de Stripe. Si quieres
que el checkout muestre una descripción, dos opciones sin tocar código:

- Editar la descripción del Price directamente en el dashboard de Stripe
  (más rápido, cero riesgo).
- O añadir `description=...` al `line_items` en el código (cambio de una
  línea, pero toca el flujo de pago real — mejor probarlo en modo TEST
  antes de tocar `main`, así que lo dejo como sugerencia y no lo aplico en
  esta sesión).

Texto sugerido para esa descripción (funciona en ambos casos):

```
Acceso VIP a Tipster IA: análisis táctico ilimitado con Claude AI,
pronóstico con stake recomendado y grupo VIP exclusivo en Telegram.
```

## Hueco para prueba social real (rellenar cuando exista)

```
[PENDIENTE — no rellenar con datos inventados]
Cuando tengas los primeros análisis con resultado real conocido
(acertado o fallado, ambos sirven para credibilidad si se muestran con
honestidad), esta sección puede llevar 2-3 ejemplos reales con fecha,
partido y resultado verificable.
```
