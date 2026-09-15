from fastapi import FastAPI

# 1. Les imports d'abord
from app.core.db import Base, engine
from app.models.lead import Lead  # noqa: F401
from app.models.user import User  # noqa: F401
from app.api.leads import router as leads_router
from app.api.auth import router as auth_router


# 3. Création de l'app  ← DOIT venir avant les include_router
app = FastAPI(title="Lead Qualifier API", version="0.1.0")

# 4. Enregistrement des routeurs  ← APRÈS la création de app
app.include_router(leads_router)
app.include_router(auth_router)


# 5. Routes éventuelles
@app.get("/health")
def health():
    return {"status": "ok"}