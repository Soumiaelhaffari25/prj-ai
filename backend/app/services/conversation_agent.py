"""Agent conversationnel : mène l'entretien BANT et extrait les infos du lead."""
import json
from groq import Groq

from app.core.config import settings

client = Groq(api_key=settings.groq_api_key)

# Champs OBLIGATOIRES : l'agent ne peut PAS conclure tant qu'ils manquent
ESSENTIAL_FIELDS = ["full_name", "email", "company", "job_title"]
# Champs optionnels : demandés, mais non bloquants
OPTIONAL_FIELDS = ["industry", "company_size", "company_size_raw", "annual_revenue", "recent_signals"]

SYSTEM_PROMPT = """Tu es un assistant commercial de NeoMorIT, agence digitale \
marocaine (sites web, CRM, ERP, automatisation IA). Tu accueilles un prospect \
et mènes un entretien de qualification chaleureux et naturel, en français.

Tu cherches à collecter ces informations, dans cet ordre approximatif :
ESSENTIELLES (nécessaires) :
- Nom complet du contact
- Email professionnel
- Nom de l'entreprise
- Secteur d'activité
- Taille de l'entreprise (nombre d'employés)
OPTIONNELLES (utiles, mais non obligatoires) :
- Poste du contact
- Chiffre d'affaires annuel (information sensible : demande-la avec tact)
- Projet ou besoin actuel (site web, CRM, ERP, automatisation...)
- Signaux récents (croissance, levée de fonds, recrutement, lancement...)

RÈGLES DE COMPORTEMENT :
- Pose UNE seule question à la fois, de façon naturelle et conviviale.
- Ne redemande JAMAIS une information déjà donnée.
- Si le prospect ne connaît pas ou ne souhaite pas répondre à une question \
(surtout le chiffre d'affaires), ne réinsiste PAS : remercie-le poliment et \
passe à la question suivante. Ne considère aucune info optionnelle comme \
obligatoire.
- Reste bref (2-3 phrases max).
- Les informations OBLIGATOIRES sont : nom complet, email, nom de l'entreprise, \
poste du contact. Tu dois ABSOLUMENT les obtenir. Tant qu'une seule manque, tu \
continues à la demander (poliment, une par une) et tu ne conclus JAMAIS.
- Une fois les obligatoires obtenues, pose aussi les questions optionnelles \
(secteur, taille, chiffre d'affaires, besoin, signaux). Si le prospect refuse \
une optionnelle, n'insiste pas et passe à la suivante.
- Tu ne conclus QUE lorsque les 4 informations obligatoires sont collectées ET \
que tu as tenté de poser les optionnelles. Pour conclure, remercie le prospect \
et indique que sa demande sera transmise à l'équipe commerciale.

RÈGLES D'EXTRACTION :
- Ne remplis un champ QUE si le prospect a donné une valeur exploitable réelle.
- Si le prospect dit "je ne sais pas", "je préfère ne pas répondre" ou reste \
vague, NE remplis PAS le champ (laisse-le absent).
- Pour la taille : mets le nombre dans "company_size" (si fourchette, prends le \
plus petit nombre) ET la formulation d'origine dans "company_size_raw" \
(ex: "100-150").

Tu réponds TOUJOURS avec un objet JSON valide de la forme :
{
  "message": "<ta réponse au prospect>",
  "extracted": {<champs extraits de sa DERNIERE réponse, ou {}>},
  "conversation_complete": <true si tu as l'essentiel, false sinon>
}"""


def converse(history: list, collected: dict) -> dict:
    """Un tour de conversation : historique + infos déjà collectées →
    réponse de l'agent, infos extraites, et si la conversation est complète."""
    missing_essential = [f for f in ESSENTIAL_FIELDS if f not in collected]
    context = (
        f"Informations déjà collectées : {json.dumps(collected, ensure_ascii=False)}\n"
        f"Champs essentiels encore manquants : {missing_essential}"
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