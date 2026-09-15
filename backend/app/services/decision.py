"""Branchement décisionnel selon le score global."""

# Seuils de décision (ajustables selon la stratégie commerciale)
THRESHOLD_QUALIFIED = 70   # >= 70 : lead chaud, à traiter en priorité
THRESHOLD_NURTURE = 40     # 40-69 : à nurturer ; < 40 : rejeté


def decide(score: int) -> dict:
    """Transforme un score 0-100 en décision commerciale explicable."""
    if score >= THRESHOLD_QUALIFIED:
        status = "qualifié"
        rationale = f"Score {score} ≥ {THRESHOLD_QUALIFIED} : lead prioritaire."
    elif score >= THRESHOLD_NURTURE:
        status = "à nurturer"
        rationale = (
            f"Score {score} entre {THRESHOLD_NURTURE} et {THRESHOLD_QUALIFIED} : "
            "potentiel à maturer."
        )
    else:
        status = "rejeté"
        rationale = f"Score {score} < {THRESHOLD_NURTURE} : hors cible."

    return {"status": status, "rationale": rationale, "threshold_applied": {
        "qualified": THRESHOLD_QUALIFIED, "nurture": THRESHOLD_NURTURE,
    }}