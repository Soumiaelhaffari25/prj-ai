from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- 1. Tous les imports d'abord ---
from app.core.db import Base, engine
from app.models.lead import Lead  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.conversation import Conversation  # noqa: F401
from app.api.leads import router as leads_router
from app.api.auth import router as auth_router
from app.api.conversation import router as chat_router

# --- 2. Création de l'app (AVANT tout include_router) ---
app = FastAPI(title="Lead Qualifier API", version="0.1.0")

# --- 3. CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Enregistrement des routeurs (APRÈS la création de app) ---
app.include_router(leads_router)
app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok"}