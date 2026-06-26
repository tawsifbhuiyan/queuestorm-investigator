from enum import Enum

class Language(str, Enum):
    EN = "en"
    BN = "bn"
    MIXED = "mixed"

class Channel(str, Enum):
    IN_APP_CHAT = "in_app_chat"
    CALL_CENTER = "call_center"
    EMAIL = "email"
    MERCHANT_PORTAL = "merchant_portal"
    FIELD_AGENT = "field_agent"

class UserType(str, Enum):
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    AGENT = "agent"
    UNKNOWN = "unknown"

class TransactionType(str, Enum):
    TRANSFER = "transfer"
    PAYMENT = "payment"
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"
    SETTLEMENT = "settlement"
    REFUND = "refund"

class TransactionStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    REVERSED = "reversed"

class EvidenceVerdict(str, Enum):
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    INSUFFICIENT_DATA = "insufficient_data"

class CaseType(str, Enum):
    WRONG_TRANSFER = "wrong_transfer"
    PAYMENT_FAILED = "payment_failed"
    REFUND_REQUEST = "refund_request"
    DUPLICATE_PAYMENT = "duplicate_payment"
    MERCHANT_SETTLEMENT_DELAY = "merchant_settlement_delay"
    AGENT_CASH_IN_ISSUE = "agent_cash_in_issue"
    PHISHING_OR_SOCIAL_ENGINEERING = "phishing_or_social_engineering"
    OTHER = "other"

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Department(str, Enum):
    CUSTOMER_SUPPORT = "customer_support"
    DISPUTE_RESOLUTION = "dispute_resolution"
    PAYMENTS_OPS = "payments_ops"
    MERCHANT_OPERATIONS = "merchant_operations"
    AGENT_OPERATIONS = "agent_operations"
    FRAUD_RISK = "fraud_risk"


DEPARTMENT_MAPPING = {
    CaseType.WRONG_TRANSFER: Department.DISPUTE_RESOLUTION,
    CaseType.PAYMENT_FAILED: Department.PAYMENTS_OPS,
    CaseType.REFUND_REQUEST: Department.CUSTOMER_SUPPORT,
    CaseType.DUPLICATE_PAYMENT: Department.PAYMENTS_OPS,
    CaseType.MERCHANT_SETTLEMENT_DELAY: Department.MERCHANT_OPERATIONS,
    CaseType.AGENT_CASH_IN_ISSUE: Department.AGENT_OPERATIONS,
    CaseType.PHISHING_OR_SOCIAL_ENGINEERING: Department.FRAUD_RISK,
    CaseType.OTHER: Department.CUSTOMER_SUPPORT,
}


SEVERITY_MAPPING = {
    CaseType.WRONG_TRANSFER: Severity.HIGH,
    CaseType.PAYMENT_FAILED: Severity.HIGH,
    CaseType.REFUND_REQUEST: Severity.LOW,
    CaseType.DUPLICATE_PAYMENT: Severity.HIGH,
    CaseType.MERCHANT_SETTLEMENT_DELAY: Severity.MEDIUM,
    CaseType.AGENT_CASH_IN_ISSUE: Severity.HIGH,
    CaseType.PHISHING_OR_SOCIAL_ENGINEERING: Severity.CRITICAL,
    CaseType.OTHER: Severity.LOW,
}