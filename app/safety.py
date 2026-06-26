import re
from typing import Tuple, List, Optional

class SafetyChecker:
    """Safety guardrails for customer replies"""
    
    FORBIDDEN_PATTERNS = {
        'pin': re.compile(r'(?:share|give|enter|provide|send|tell|type|input)\s+(?:your\s+)?(?:pin|password|otp|code|secret|credential)', re.IGNORECASE),
        'refund_promise': re.compile(r'(?:we\s+will\s+refund|we\'ll\s+refund|we\s+guarantee\s+refund|will\s+reverse|confirmed\s+refund)', re.IGNORECASE),
        'third_party': re.compile(r'(?:contact|call|reach\s+out\s+to)\s+(?:[0-9]{10,}|[^\s]+@[^\s]+|[a-zA-Z]+\s+[a-zA-Z]+\s+number)', re.IGNORECASE),
    }
    
    @classmethod
    def check_safety(cls, reply: str) -> Tuple[bool, List[str]]:
        """Check if reply violates safety rules."""
        violations = []
        
        if cls.FORBIDDEN_PATTERNS['pin'].search(reply):
            violations.append("Request for PIN/OTP/password detected")
        
        if cls.FORBIDDEN_PATTERNS['refund_promise'].search(reply):
            violations.append("Unauthorized refund/reversal promise detected")
        
        if cls.FORBIDDEN_PATTERNS['third_party'].search(reply):
            violations.append("Suspicious third-party contact instruction detected")
        
        return len(violations) == 0, violations
    
    @classmethod
    def get_safe_customer_reply(cls, case_type: str, verdict: str, 
                                 transaction_id: Optional[str] = None) -> str:
        """Generate a safe customer reply template"""
        
        tx_part = f" transaction {transaction_id}" if transaction_id else ""
        
        base_templates = {
            'wrong_transfer': f"We have noted your concern about{tx_part}. Please do not share your PIN or OTP with anyone. Our dispute team will review the case and contact you through official support channels.",
            'payment_failed': f"We have noted that{tx_part} may have caused an unexpected balance deduction. Our payments team will review the case and any eligible amount will be returned through official channels. Please do not share your PIN or OTP with anyone.",
            'refund_request': f"Thank you for reaching out. Refunds for completed merchant payments depend on the merchant's own policy. We recommend contacting the merchant directly. If you need help reaching them, please reply and we will guide you. Please do not share your PIN or OTP with anyone.",
            'duplicate_payment': f"We have noted the possible duplicate payment for{tx_part}. Our payments team will verify with the biller and any eligible amount will be returned through official channels. Please do not share your PIN or OTP with anyone.",
            'merchant_settlement_delay': f"We have noted your concern about settlement{tx_part}. Our merchant operations team will check the batch status and update you on the expected settlement time through official channels.",
            'agent_cash_in_issue': f"We have noted your concern about cash-in{tx_part}. Our agent operations team will verify the transaction and provide an update through official channels. Please do not share your PIN or OTP with anyone.",
            'phishing_or_social_engineering': "Thank you for reaching out before sharing any information. We never ask for your PIN, OTP, or password under any circumstances. Please do not share these with anyone, even if they claim to be from us. Our fraud team has been notified of this incident.",
            'other': f"We have received your request. Please do not share your PIN or OTP with anyone. Our support team will review your case and contact you through official support channels."
        }
        
        return base_templates.get(case_type, base_templates['other'])