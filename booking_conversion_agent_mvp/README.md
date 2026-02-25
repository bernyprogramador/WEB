# Booking Conversion Agent (Villas) – MVP v1

Implementación MVP enfocada en velocidad de respuesta, scoring determinista, escalado humano y trazabilidad completa sobre Google Sheets.

## Entregables
- Plantilla Google Sheets (Leads, Messages, Villas_KB, Settings): `templates/*.csv`
- Flujos n8n (3 escenarios): `workflows/*.json`
- Motor determinista (scoring, guardrails, brief): `src/agent_engine.py`
- Simulación QA de 20 leads: `tests/simulate_20_leads.py`
- Documentación operativa 1 página: `docs/ONE_PAGER_SETUP.md`
- Plantillas de mensajes ES/EN: `templates/message_templates.md`

## Ejecutar prueba de aceptación rápida
```bash
python3 booking_conversion_agent_mvp/tests/simulate_20_leads.py
```
