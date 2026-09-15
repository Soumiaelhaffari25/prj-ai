"""Tâche asynchrone d'enrichissement."""
import json

from app.core.celery_app import celery_app
from app.core.db import SessionLocal
from app.models.lead import Lead
from app.services.enrichment import enrich_lead


@celery_app.task(name="enrich_lead_task")
def enrich_lead_task(lead_id: str) -> dict:
    """Récupère le lead, l'enrichit, et met à jour la base."""
    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if lead is None:
            return {"status": "error", "message": "Lead introuvable"}

        # On passe les données actuelles à l'enrichissement
        current = {
            "email": lead.email,
            "job_title": lead.job_title,
        }
        enriched = enrich_lead(current)

        # On ne remplace que les champs vides (on ne surdécrit pas l'existant)
        if not lead.industry:
            lead.industry = enriched["industry"]
        if not lead.company_size:
            lead.company_size = enriched["company_size"]
        if not lead.annual_revenue:
            lead.annual_revenue = enriched["annual_revenue"]
        if not lead.recent_signals:
            lead.recent_signals = enriched["recent_signals"]
        if not lead.job_title:
            lead.job_title = enriched["job_title"]

        lead.status = "enrichi"
        db.commit()
        return {"status": "ok", "lead_id": lead_id, "source": enriched["enrichment_source"]}
    finally:
        db.close()