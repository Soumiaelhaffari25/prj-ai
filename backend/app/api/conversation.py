"""Routes de l'agent conversationnel (vue chatbot publique, sans auth)."""
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.conversation import Conversation
from app.models.lead import Lead
from app.services.conversation_agent import converse, REQUIRED_FIELDS
from app.services.normalization import normalize_lead_data, validate_lead_email
from app.graph.pipeline import pipeline

router = APIRouter(prefix="/chat", tags=["chat"])


class MessageIn(BaseModel):
    conversation_id: str | None = None
    message: str


@router.post("/start")
def start_conversation(db: Session = Depends(get_db)):
    """Démarre une nouvelle conversation et renvoie le message d'accueil."""
    conv = Conversation()
    # Message d'accueil initial (sans appeler le LLM)
    greeting = (
        "Bonjour et bienvenue chez NeoMorIT ! Je suis là pour comprendre votre "
        "projet digital. Pour commencer, pouvez-vous me dire votre nom et le nom "
        "de votre entreprise ?"
    )
    history = [{"role": "assistant", "content": greeting}]
    conv.messages = json.dumps(history, ensure_ascii=False)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"conversation_id": conv.id, "message": greeting}


@router.post("/message")
def send_message(payload: MessageIn, db: Session = Depends(get_db)):
    """Envoie un message du prospect et renvoie la réponse de l'agent."""
    conv = db.get(Conversation, payload.conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    history = json.loads(conv.messages)
    collected = json.loads(conv.collected_data)

    # Ajoute le message du prospect à l'historique
    history.append({"role": "user", "content": payload.message})

    # L'agent répond
    result = converse(history, collected)

    # Met à jour les infos collectées
    collected.update(result.get("extracted", {}))

    # Ajoute la réponse de l'agent à l'historique
    history.append({"role": "assistant", "content": result["message"]})

    conv.messages = json.dumps(history, ensure_ascii=False)
    conv.collected_data = json.dumps(collected, ensure_ascii=False)

    lead_created = None
    # Si la conversation est complète, on crée et on score le lead
    if result.get("conversation_complete") and conv.status == "en_cours":
        lead_created = _create_and_score_lead(db, collected)
        conv.status = "terminée"
        conv.lead_id = lead_created

    db.commit()
    return {
        "conversation_id": conv.id,
        "message": result["message"],
        "complete": result.get("conversation_complete", False),
        "lead_id": lead_created,
    }


def _create_and_score_lead(db: Session, collected: dict) -> str | None:
    """Crée le lead à partir des infos collectées, puis le score (pipeline)."""
    # Validation minimale : il faut au moins un email valide
    email = collected.get("email", "")
    is_valid, _ = validate_lead_email(email) if email else (False, "")
    if not is_valid:
        return None

    data = normalize_lead_data({
        "full_name": collected.get("full_name", "Prospect"),
        "email": email,
        "company": collected.get("company"),
        "industry": collected.get("industry"),
        "company_size": collected.get("company_size"),
        "job_title": collected.get("job_title"),
        "recent_signals": collected.get("recent_signals"),
        "source": "chatbot",
    })
    lead = Lead(**data)
    lead.validation_status = "validé"
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Scoring automatique via le pipeline
    final_state = pipeline.invoke({
        "lead": lead, "rag_context": None, "score_result": None,
        "decision": None, "action": None,
    })
    lead.score = final_state["score_result"]["score"]
    lead.score_details = json.dumps(final_state["score_result"], ensure_ascii=False)
    lead.status = final_state["decision"]["status"]
    action = final_state.get("action")
    if action:
        lead.assigned_to = action.get("assigned_to")
        lead.action_message = action.get("message")
    db.commit()
    return lead.id