# Booking Conversion Agent (Villas) – MVP v1

## Stack elegida
- **Automatización:** n8n (rápido de desplegar, versionable, confiable con retries).
- **DB operativa:** Google Sheets (tabs: Leads, Messages, Villas_KB, Settings).
- **IA:** 1 modelo LLM con KB estricta por villa (sin inventar precios/disponibilidad).
- **Canales:** Web form por webhook (v1). WhatsApp vía Twilio/360dialog en v1.1.

## Setup rápido (lista para usar)
1. Crea una Google Sheet nueva y añade 4 tabs usando los CSV de `templates/`.
2. Importa en n8n los 3 workflows de `workflows/`.
3. Configura credenciales en n8n:
   - Google Sheets OAuth.
   - Proveedor WhatsApp/API (Twilio u otro).
   - SMTP o Slack webhook.
4. En `Settings` completa: manager_phone, manager_email, llm_model, api key.
5. Activa workflows en orden: Scenario 3, Scenario 2, Scenario 1.

## Cómo cambiar KB por villa
- Ir a tab **Villas_KB** y editar la fila de `villa_id`.
- Campos críticos:
  - `tone_guidelines`: define tono premium.
  - `faq` y `policies`: solo datos confirmados.
  - `allowed_price_range_text`: rango orientativo permitido.
  - `policies_fully_defined`: TRUE solo si políticas sensibles están completas.

## Activar/desactivar follow-ups
- Opción A: desactivar nodo “Schedule/Reschedule Followups” en workflows 1 y 2.
- Opción B: en `Settings`, dejar vacías plantillas `followup_*`; el flujo no envía mensajes.

## Cómo ver leads HOT hoy
- En tab **Leads** crear filtro:
  - `score = HOT`
  - `fecha = hoy`
  - `status != HUMAN_REQUIRED`
- Ordenar por `ultima_interaccion` descendente para priorizar callbacks.

## Reglas de guardrail
- Nunca responder con precio exacto, disponibilidad exacta o descuentos fuera de KB.
- Si falta dato: preguntar (máx 6 preguntas).
- Si piden exactitud/negociación/pago/políticas sensibles/conflicto: **HUMAN_REQUIRED** + alerta inmediata.

## Logging y fiabilidad
- Cada mensaje entra en tab `Messages`.
- Cada actualización de lead en tab `Leads` con `ultima_interaccion` y `proximo_followup`.
- En n8n: activar “Retry on Fail” (3 intentos, backoff exponencial) + flujo de error a hoja `Dead_Letter` (opcional).
