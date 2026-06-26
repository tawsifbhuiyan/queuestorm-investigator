from pydantic import BaseModel, Field, validator
from typing import Optional, List
from app.constants import *

class Transaction(BaseModel):
    transaction_id: str
    timestamp: str
    type: TransactionType
    amount: float
    counterparty: str
    status: TransactionStatus

class AnalyzeRequest(BaseModel):
    ticket_id: str
    complaint: str
    language: Optional[Language] = None
    channel: Optional[Channel] = None
    user_type: Optional[UserType] = None
    campaign_context: Optional[str] = None
    transaction_history: Optional[List[Transaction]] = None
    metadata: Optional[dict] = None

    @validator('complaint')
    def validate_complaint(cls, v):
        if not v or not v.strip():
            raise ValueError('Complaint cannot be empty')
        return v.strip()

class AnalyzeResponse(BaseModel):
    ticket_id: str
    relevant_transaction_id: Optional[str] = None
    evidence_verdict: EvidenceVerdict
    case_type: CaseType
    severity: Severity
    department: Department
    agent_summary: str
    recommended_next_action: str
    customer_reply: str
    human_review_required: bool
    confidence: Optional[float] = None
    reason_codes: Optional[List[str]] = None