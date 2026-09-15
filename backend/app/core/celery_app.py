"""Configuration de l'application Celery (traitement asynchrone)."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "lead_qualifier",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)

# Import explicite des tâches pour garantir leur enregistrement au démarrage.
# (plus fiable que autodiscover sur Windows / selon la structure du projet)
import app.tasks.enrichment_task  # noqa: E402, F401