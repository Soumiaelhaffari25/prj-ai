"""Couche 1 du scoring : règles déterministes BANT."""

TARGET_INDUSTRIES = {"saas", "fintech", "logiciel", "technologie", "e-commerce"}

EXECUTIVE_TITLES = {
    "ceo", "cto", "cfo", "coo", "founder", "fondateur", "fondatrice",
    "directeur général", "directrice générale", "général", "générale",
    "président", "présidente", "pdg", "dg", "gérant", "gérante",
}
DIRECTOR_TITLES = {
    "directeur", "directrice", "director", "vp", "head",
    "responsable", "chef",
}

WEIGHTS = {"budget": 0.25, "authority": 0.30, "need": 0.30, "timing": 0.15}


def score_budget(company_size: int | None, annual_revenue: float | None) -> int:
    """Adéquation taille + CA de l'entreprise."""
    if company_size is None and annual_revenue is None:
        return 0
    score = 0
    if company_size is not None:
        if company_size >= 200:
            score += 50
        elif company_size >= 50:
            score += 35
        elif company_size >= 10:
            score += 20
        else:
            score += 10
    if annual_revenue is not None:
        if annual_revenue >= 10_000_000:
            score += 50
        elif annual_revenue >= 1_000_000:
            score += 35
        elif annual_revenue >= 100_000:
            score += 20
        else:
            score += 10
    return min(score, 100)


def score_authority(job_title: str | None) -> int:
    """Niveau décisionnel du contact."""
    if not job_title:
        return 0
    title = job_title.lower()
    if any(t in title for t in EXECUTIVE_TITLES):
        return 100
    if any(t in title for t in DIRECTOR_TITLES):
        return 65
    return 30


def score_need(industry: str | None) -> int:
    """Correspondance secteur / cible."""
    if not industry:
        return 0
    return 100 if industry.lower() in TARGET_INDUSTRIES else 25


def score_timing(recent_signals: str | None) -> int:
    """Présence de signaux d'intention récents."""
    if not recent_signals or not recent_signals.strip():
        return 20  # neutre : pas de signal n'est pas rédhibitoire
    return 90


def compute_bant_score(lead) -> dict:
    """Calcule les 4 sous-scores, le score global pondéré et la justification."""
    subscores = {
        "budget": score_budget(lead.company_size, lead.annual_revenue),
        "authority": score_authority(lead.job_title),
        "need": score_need(lead.industry),
        "timing": score_timing(lead.recent_signals),
    }
    global_score = round(
        sum(subscores[k] * WEIGHTS[k] for k in WEIGHTS)
    )
    return {
        "score": global_score,
        "subscores": subscores,
        "weights": WEIGHTS,
        "explanation": {
            "budget": f"Taille={lead.company_size}, CA={lead.annual_revenue} → {subscores['budget']}/100",
            "authority": f"Poste='{lead.job_title}' → {subscores['authority']}/100",
            "need": f"Secteur='{lead.industry}' → {subscores['need']}/100",
            "timing": f"Signaux='{lead.recent_signals}' → {subscores['timing']}/100",
        },
    }
    
from app.services.llm_scoring import score_with_llm

# Pondération entre les deux couches (somme = 1.0)
LAYER_WEIGHTS = {"bant": 0.6, "llm": 0.4}


def compute_hybrid_score(lead, rag_context: str | None = None) -> dict:
    """Score final = BANT (déterministe) + LLM (qualitatif, éclairé par le RAG)."""
    bant = compute_bant_score(lead)
    llm = score_with_llm(lead, rag_context=rag_context)

    final = round(
        LAYER_WEIGHTS["bant"] * bant["score"]
        + LAYER_WEIGHTS["llm"] * llm["score"]
    )
    return {
        "score": final,
        "layer_weights": LAYER_WEIGHTS,
        "bant": bant,
        "llm": llm,
    }