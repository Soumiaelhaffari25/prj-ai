"""Agent conversationnel : mène l'entretien BANT et extrait les infos du lead."""
import json
from groq import Groq

from app.core.config import settings

client = Groq(api_key=settings.groq_api_key)

# Les champs qu'on cherche à collecter au fil de la conversation
REQUIRED_FIELDS = ["full_name", "email", "company", "industry", "company_size", "job_title", "recent_signals"]

SYSTEM_PROMPT = """Tu es un assistant commercial de NeoMorIT, agence digitale \
marocaine (sites web, CRM, ERP, automatisation IA). Tu accueilles un prospect \
et mènes un entretien de qualification chaleureux et naturel, en français.

Ton objectif est de collecter progressivement ces informations :
- Nom complet du contact
- Email professionnel
- Nom de l'entreprise
- Secteur d'activité
- Taille de l'entreprise (nombre d'employés)
- Poste du contact
- Projet ou besoin actuel, signaux récents (croissance, levée de fonds...)

Règles :
- Pose UNE seule question à la fois, de façon naturelle et conviviale.
- Ne redemande jamais une information déjà donnée.
- Reste bref (2-3 phrases max par message).
- Quand tu as collecté l'essentiel (au moins nom, email, entreprise, secteur, \
taille), remercie le prospect et indique que sa demande va être transmise à \
l'équipe commerciale.

Tu réponds TOUJOURS avec un objet JSON valide de la forme :
{
  "message": "<ta réponse au prospect>",
  "extracted": {<les champs que tu as pu extraire de sa DERNIERE réponse, ou {}>},
  "conversation_complete": <true si tu as l'essentiel, false sinon>
}"""


def converse(history: list, collected: dict) -> dict:
    """Un tour de conversation : prend l'historique + les infos déjà collectées,
    renvoie la réponse de l'agent, les nouvelles infos extraites, et si c'est fini."""
    context = (
        f"Informations déjà collectées : {json.dumps(collected, ensure_ascii=False)}\n"
        f"Champs encore manquants : {[f for f in REQUIRED_FIELDS if f not in collected]}"
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "system", "content": context})
    messages.extend(history)

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        result.setdefault("message", "Pouvez-vous préciser ?")
        result.setdefault("extracted", {})
        result.setdefault("conversation_complete", False)
        return result
    except Exception as e:
        return {
            "message": "Désolé, un souci technique est survenu. Pouvez-vous répéter ?",
            "extracted": {},
            "conversation_complete": False,
            "error": str(e),
        }