"""Couche 2 du scoring : jugement qualitatif par LLM (Groq/Llama)."""
import json
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """Tu es un analyste commercial expert en qualification de leads B2B.
Tu évalues la qualité d'un prospect sur des critères QUALITATIFS que les règles \
automatiques ne captent pas : intention réelle, urgence, cohérence du profil, \
signaux faibles.

Tu réponds UNIQUEMENT avec un objet JSON valide, sans texte autour, de la forme :
{
  "score": <entier 0-100>,
  "reasoning": "<explication concise en français, 2-3 phrases>",
  "intent_level": "<faible|moyen|fort>",
  "risk_flags": ["<éventuels signaux négatifs>"]
}"""


def score_with_llm(lead, rag_context: str | None = None) -> dict:
    """Évaluation qualitative structurée du lead, éclairée par le contexte RAG."""
    context_block = ""
    if rag_context:
        context_block = (
            "\n\nContexte de référence (profil client idéal, cas clients, "
            "playbook de NeoMorIT) :\n" + rag_context
        )

    lead_context = f"""Prospect à évaluer :
- Nom : {lead.full_name}
- Entreprise : {lead.company}
- Poste : {lead.job_title}
- Secteur : {lead.industry}
- Taille entreprise : {lead.company_size}
- Chiffre d'affaires : {lead.annual_revenue}
- Signaux récents : {lead.recent_signals}{context_block}

Évalue ce prospect en le comparant au contexte de référence ci-dessus."""

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": lead_context},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        result = json.loads(raw)
        result["score"] = max(0, min(100, int(result.get("score", 0))))
        result.setdefault("reasoning", "")
        result.setdefault("intent_level", "moyen")
        result.setdefault("risk_flags", [])
        return result
    except Exception as e:
        return {
            "score": 0,
            "reasoning": f"Évaluation LLM indisponible : {e}",
            "intent_level": "inconnu",
            "risk_flags": ["llm_error"],
            "error": True,
        }