import json
from app.services.scoring import compute_bant_score
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadRead

from app.services.scoring import compute_hybrid_score

from app.graph.pipeline import pipeline

from app.services.rag import build_index, retrieve_context
from app.services.normalization import (
    normalize_lead_data, validate_lead_email, find_duplicate,
)
from app.tasks.enrichment_task import enrich_lead_task
from app.core.auth import get_current_user
from app.models.user import User

from datetime import datetime, timezone
from app.schemas.lead import LeadReview 

from fastapi import WebSocket, WebSocketDisconnect
from app.core.ws_manager import manager

router = APIRouter(prefix="/leads", tags=["leads"])

@router.post("", response_model=LeadRead, status_code=201)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()

    # 1. Normalisation
    data = normalize_lead_data(data)

    # 2. Validation email
    is_valid, message = validate_lead_email(data["email"])
    if not is_valid:
        raise HTTPException(status_code=422, detail=message)

    # 3. Déduplication
    existing = find_duplicate(db, data["email"])
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Lead déjà existant (id={existing.id})",
        )

    lead = Lead(**data)
    lead.validation_status = "validé"
    lead.validation_message = message
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead introuvable")
    return lead


@router.get("", response_model=list[LeadRead])
def list_leads(db: Session = Depends(get_db)):
    return db.query(Lead).order_by(Lead.created_at.desc()).all()

@router.post("/{lead_id}/process", response_model=LeadRead)
def process_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead introuvable")

    # exécution du graphe LangGraph
    final_state = pipeline.invoke({
        "lead": lead, "rag_context": None, "score_result": None,
        "decision": None, "action": None,
    })

    lead.score = final_state["score_result"]["score"]
    lead.score_details = json.dumps(final_state["score_result"], ensure_ascii=False)
    lead.status = final_state["decision"]["status"]

    # Persistance de l'action si elle a été générée
    action = final_state.get("action")
    if action:
        lead.assigned_to = action.get("assigned_to")
        lead.action_message = action.get("message")

    db.commit()
    db.refresh(lead)
    return lead

@router.post("/admin/reindex")
def reindex_knowledge_base(current_user: User = Depends(get_current_user)):
    count = build_index()
    return {"status": "ok", "documents_indexed": count, "by": current_user.email}

@router.post("/{lead_id}/enrich")
def trigger_enrichment(lead_id: str, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead introuvable")

    # Dépose la tâche dans la file ; ne bloque pas
    task = enrich_lead_task.delay(lead_id)
    return {"status": "enrichissement lancé", "task_id": task.id}

@router.post("/{lead_id}/review", response_model=LeadRead)
def review_lead(
    lead_id: str,
    payload: LeadReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead introuvable")

    if payload.action == "valider":
        lead.review_status = "validé"
        # si le commercial a édité le message, on garde sa version
        if payload.edited_message is not None:
            lead.action_message = payload.edited_message
    elif payload.action == "rejeter":
        lead.review_status = "rejeté"
    else:
        raise HTTPException(status_code=422, detail="Action invalide (valider ou rejeter)")

    lead.reviewed_by = current_user.email
    lead.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)
    return lead

@router.websocket("/ws")
async def leads_websocket(websocket: WebSocket):
    """Le dashboard se connecte ici pour recevoir les mises à jour en temps réel."""
    await manager.connect(websocket)
    try:
        while True:
            # On garde la connexion ouverte (on attend, sans rien faire de spécial)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)