"""Observabilité : client Langfuse pour tracer les appels LLM."""
from langfuse import Langfuse

from app.core.config import settings

# On active Langfuse seulement si les clés sont renseignées
_enabled = bool(settings.langfuse_public_key and settings.langfuse_secret_key)

if _enabled:
    langfuse = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )
else:
    langfuse = None


def is_enabled() -> bool:
    return _enabled