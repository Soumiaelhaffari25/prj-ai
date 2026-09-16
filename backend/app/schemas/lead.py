from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class LeadCreate(BaseModel):
    full_name: str
    email: EmailStr
    company: str | None = None
    source: str = "api"
    job_title: str | None = None
    industry: str | None = None
    company_size: int | None = None
    annual_revenue: float | None = None
    recent_signals: str | None = None


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
   
    id: str
    full_name: str
    email: str
    company: str | None
    status: str
    source: str
    job_title: str | None
    industry: str | None
    company_size: int | None
    company_size_raw: str | None
    annual_revenue: float | None
    recent_signals: str | None
    score: int | None
    score_details: str | None
    created_at: datetime
    validation_status: str | None
    validation_message: str | None
    assigned_to: str | None
    action_message: str | None
    review_status: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None


class LeadReview(BaseModel):
    action: str                          # "valider" | "rejeter"
    edited_message: str | None = None    # message édité (optionnel)