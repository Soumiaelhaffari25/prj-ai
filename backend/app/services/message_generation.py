"""Étape 7 (partie message) : génération d'un message d'approche personnalisé."""
from groq import Groq

from app.core.config import settings

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """Tu es un commercial expert de NeoMorIT, agence digitale \
(sites web, CRM, ERP, automatisation IA). Tu rédiges un court message \
d'approche personnalisé (email) à un prospect qualifié.

Règles :
- Ton professionnel, chaleureux, jamais agressif.
- Personnalise selon le secteur, le poste et les signaux du prospect.
- Mentionne une valeur concrète que NeoMorIT peut apporter à son contexte.
- 4 à 6 phrases maximum. Pas de formule creuse.
- Termine par une proposition d'échange (appel/rendez-vous).
- Réponds UNIQUEMENT avec le texte du message, sans objet ni signature."""


def generate_message(lead, rag_context: str | None = None) -> dict:
    """Génère un message d'approche personnalisé pour un lead qualifié."""
    context = f"""Prospect :
- Nom : {lead.full_name}
- Entreprise : {lead.company}
- Poste : {lead.job_title}
- Secteur : {lead.industry}
- Taille : {lead.company_size}
- Signaux récents : {lead.recent_signals}"""

    if rag_context:
        context += f"\n\nContexte NeoMorIT (offre, cas clients) :\n{rag_context}"

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=0.7,  # un peu de créativité pour la rédaction
        )
        message = response.choices[0].message.content.strip()
        return {"message": message, "generated": True}
    except Exception as e:
        return {"message": "", "generated": False, "error": str(e)}