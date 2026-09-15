"""Normalisation, validation et déduplication."""
import re
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session

from app.models.lead import Lead


def normalize_lead_data(data: dict) -> dict:
    """Nettoie et uniformise les champs d'un lead."""
    cleaned = dict(data)

    # Email : minuscules + suppression des espaces
    if cleaned.get("email"):
        cleaned["email"] = cleaned["email"].strip().lower()

    # Nom : espaces multiples réduits, bords nettoyés
    if cleaned.get("full_name"):
        cleaned["full_name"] = re.sub(r"\s+", " ", cleaned["full_name"]).strip()

    # Entreprise : nettoyage + retrait des suffixes juridiques courants
    if cleaned.get("company"):
        company = re.sub(r"\s+", " ", cleaned["company"]).strip()
        company = re.sub(
            r"\b(SARL|SA|SAS|SASU|EURL|Inc|LLC|Ltd|GmbH)\b\.?$",
            "", company, flags=re.IGNORECASE,
        ).strip()
        cleaned["company"] = company

    # Secteur : minuscules pour cohérence avec le scoring
    if cleaned.get("industry"):
        cleaned["industry"] = cleaned["industry"].strip().lower()

    return cleaned


def validate_lead_email(email: str) -> tuple[bool, str]:
    """Valide le format de l'email. Retourne (valide, message)."""
    try:
        validate_email(email, check_deliverability=False)
        return True, "Email valide"
    except EmailNotValidError as e:
        return False, f"Email invalide : {e}"


def find_duplicate(db: Session, email: str, exclude_id: str | None = None) -> Lead | None:
    """Cherche un lead existant avec le même email (hors le lead courant)."""
    query = db.query(Lead).filter(Lead.email == email)
    if exclude_id:
        query = query.filter(Lead.id != exclude_id)
    return query.first()