from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

ESCALATION_KEYWORDS = {
    "exact_availability": ["disponible", "availability", "available", "fecha exacta", "exact date"],
    "exact_price": ["precio exacto", "exact price", "tarifa exacta", "quote now"],
    "discount": ["descuento", "discount", "mejor precio", "negociar"],
    "sensitive_policies": ["cancelación", "deposit", "depósito", "pets", "mascotas", "fiesta", "party", "menores"],
    "payment_intent": ["pagar", "pay", "payment link", "book now", "reserve now"],
    "conflict": ["queja", "complaint", "terrible", "legal", "fraud"],
}


@dataclass
class Lead:
    lead_id: str
    created_at: datetime
    villa_id: str
    channel: str
    name: str = ""
    contact: str = ""
    language: str = "es"
    message: str = ""
    checkin: Optional[datetime] = None
    checkout: Optional[datetime] = None
    guests: Optional[int] = None
    budget: Optional[float] = None
    reason: Optional[str] = None
    preferences: Optional[str] = None
    explicit_intent: bool = False
    status: str = "NEW"
    score: str = "COLD"
    stage: str = "NEW_INQUIRY"
    next_followup: Optional[datetime] = None
    attempts: int = 0
    objections: List[str] = field(default_factory=list)


class BookingConversionAgent:
    def __init__(self, kb: Dict[str, Dict]):
        self.kb = kb

    def detect_language(self, message: str) -> str:
        msg = (message or "").lower()
        if any(token in msg for token in ["hello", "price", "availability", "book"]):
            return "en"
        return "es"

    def calculate_score(self, lead: Lead) -> str:
        has_dates = lead.checkin is not None and lead.checkout is not None
        days_to_checkin = (lead.checkin - datetime.utcnow()).days if lead.checkin else 999
        guests_defined = lead.guests is not None and lead.guests > 0
        budget_defined = lead.budget is not None and lead.budget > 0
        compatible_budget = budget_defined and lead.budget >= self.kb[lead.villa_id].get("min_budget", 0)

        if has_dates and days_to_checkin <= 30 and guests_defined and compatible_budget and lead.explicit_intent:
            return "HOT"
        if has_dates and (not budget_defined or not guests_defined):
            return "WARM"
        return "COLD"

    def should_escalate(self, message: str, kb_entry: Dict) -> Optional[str]:
        msg = (message or "").lower()
        for reason, keywords in ESCALATION_KEYWORDS.items():
            if any(k in msg for k in keywords):
                if reason == "sensitive_policies" and kb_entry.get("policies_fully_defined", False):
                    continue
                return reason
        return None

    def next_question(self, lead: Lead) -> Optional[str]:
        asked = [lead.checkin, lead.checkout, lead.guests, lead.budget, lead.reason, lead.preferences]
        if sum(value is not None for value in asked[:4]) >= 4:
            return None

        if lead.checkin is None or lead.checkout is None:
            return "¿Qué fechas tienes en mente para tu estancia?"
        if lead.guests is None:
            return "¿Para cuántos huéspedes sería la reserva?"
        if lead.budget is None:
            return "¿Cuál es el rango de presupuesto por noche que prefieres?"
        if lead.reason is None:
            return "¿Qué ocasión te trae a la villa (vacaciones, celebración, retiro)?"
        if lead.preferences is None:
            return "¿Tienes alguna preferencia clave (vista, chef, piscina climatizada)?"
        return None

    def initial_message(self, language: str) -> str:
        if language == "en":
            return (
                "Thank you for contacting us. I can help you shortlist the best villa in minutes. "
                "To begin, may I confirm your travel dates and number of guests?"
            )
        return (
            "Gracias por contactarnos. Te ayudo a encontrar la villa ideal en minutos. "
            "Para empezar, ¿me confirmas fechas y número de huéspedes?"
        )

    def guarded_reply(self, lead: Lead, user_message: str) -> str:
        kb_entry = self.kb[lead.villa_id]
        escalation = self.should_escalate(user_message, kb_entry)
        if "dispon" in user_message.lower() or "availability" in user_message.lower():
            return "Puedo confirmarlo en minutos. Para validarlo con precisión, te pongo ahora mismo con nuestro manager."
        if escalation:
            return "Gracias por tu mensaje. Para darte una respuesta precisa, te conecto ahora con nuestro manager."
        return self.next_question(lead) or "Perfecto, con esto preparo un resumen para confirmar opciones contigo."

    def schedule_followups(self, lead: Lead, base_time: datetime) -> List[datetime]:
        return [base_time + timedelta(minutes=30), base_time + timedelta(hours=4), base_time + timedelta(hours=24)]

    def generate_brief(self, lead: Lead, last_messages: List[str]) -> Dict[str, str]:
        summary = " | ".join(last_messages[-3:])
        key_data = (
            f"Fechas: {lead.checkin} - {lead.checkout}; Huéspedes: {lead.guests}; "
            f"Budget: {lead.budget}; Score: {lead.score}"
        )
        objections = ", ".join(lead.objections) if lead.objections else "Ninguna explícita"
        next_step = "Llamar en <10 min y confirmar disponibilidad real + propuesta cerrada"
        return {
            "summary": summary,
            "key_data": key_data,
            "objections": objections,
            "next_step": next_step,
        }
