"""Étape 3 du pipeline : enrichissement du profil du lead.

Implémentation MOCK déterministe : simule des appels à des API externes.
Interface prête pour brancher de vraies sources (Apollo, Hunter, Tavily) en
production, sans modifier l'architecture asynchrone autour.
"""
import time

# Base de référence simulée, indexée par domaine d'email.
# Déterministe : un même domaine donne toujours le même résultat.
_MOCK_DB = {
    "fintechco.ma": {
        "industry": "fintech", "company_size": 120,
        "annual_revenue": 3000000.0,
        "recent_signals": "levée de fonds série A récente",
        "job_title": "Directrice Générale",
    },
    "petiteboite.ma": {
        "industry": "restauration", "company_size": 3,
        "annual_revenue": 50000.0, "recent_signals": "",
        "job_title": "Stagiaire",
    },
}


def enrich_lead(lead_data: dict) -> dict:
    """Enrichit un lead à partir de son email (mock déterministe).

    Simule la latence d'un appel réseau. En production, remplacer le corps par
    de vrais appels Apollo / Hunter / Tavily.
    """
    # Simule la latence d'un vrai appel API (valeur fixe, pas aléatoire)
    time.sleep(2)

    email = lead_data.get("email", "")
    domain = email.split("@")[-1] if "@" in email else ""

    # Domaine connu : données déterministes. Domaine inconnu : non enrichi
    # (on n'invente pas de données pour une entreprise qu'on ne connaît pas).
    enriched = _MOCK_DB.get(domain, {
        "industry": "inconnu",
        "company_size": None,
        "annual_revenue": None,
        "recent_signals": "",
        "job_title": lead_data.get("job_title") or "inconnu",
    })

    return {
        "industry": enriched["industry"],
        "company_size": enriched["company_size"],
        "annual_revenue": enriched["annual_revenue"],
        "recent_signals": enriched["recent_signals"],
        "job_title": enriched["job_title"],
        "enrichment_source": "mock",
    }