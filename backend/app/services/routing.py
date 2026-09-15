"""Étape 7 (partie routage) : attribution du lead au bon commercial."""

# Table de routage : règles d'attribution selon le secteur.
# En production, ces règles viendraient d'une config ou d'une base.
_SECTOR_ROUTING = {
    "fintech": "Youssef El Amrani (Pôle Finance)",
    "finance": "Youssef El Amrani (Pôle Finance)",
    "e-commerce": "Salma Bennis (Pôle Retail)",
    "retail": "Salma Bennis (Pôle Retail)",
    "saas": "Karim Tazi (Pôle Tech)",
    "logiciel": "Karim Tazi (Pôle Tech)",
    "technologie": "Karim Tazi (Pôle Tech)",
}

_DEFAULT_REP = "Équipe commerciale générale"
_SENIOR_REP = "Directeur commercial (grands comptes)"


def route_lead(lead) -> dict:
    """Détermine le commercial destinataire selon secteur et taille."""
    # Les grandes entreprises vont au responsable grands comptes
    if lead.company_size and lead.company_size >= 250:
        rep = _SENIOR_REP
        reason = f"Grand compte ({lead.company_size} employés)"
    else:
        industry = (lead.industry or "").lower()
        rep = _SECTOR_ROUTING.get(industry, _DEFAULT_REP)
        reason = f"Secteur '{industry}'" if industry in _SECTOR_ROUTING else "Secteur hors table de routage"

    return {"assigned_to": rep, "routing_reason": reason}