from typing import Optional, List, Tuple, Dict, Any
import re
from app.constants import *
from app.models import AnalyzeRequest, Transaction, AnalyzeResponse
from app.safety import SafetyChecker

class QueueStormInvestigator:
    """Core investigation logic for complaint analysis"""
    
    def __init__(self):
        self.safety_checker = SafetyChecker()
    
    def investigate(self, request: AnalyzeRequest) -> AnalyzeResponse:
        """
        Main investigation pipeline
        """
        
        intent = self._parse_intent(request.complaint)
        
        
        relevant_tx, match_score = self._find_relevant_transaction(
            request.complaint, 
            request.transaction_history or []
        )
        
        #Evidence verdict er jonno
        evidence_verdict = self._determine_verdict(
            intent, 
            relevant_tx, 
            match_score, 
            request.transaction_history or []
        )
        
    
        case_type = self._classify_case(intent, relevant_tx, evidence_verdict, request)
        
        
        severity = self._determine_severity(case_type, evidence_verdict, request)
        department = DEPARTMENT_MAPPING.get(case_type, Department.CUSTOMER_SUPPORT)
        
        #Safe response er jonno
        customer_reply = self.safety_checker.get_safe_customer_reply(
            case_type.value,
            evidence_verdict.value,
            relevant_tx.transaction_id if relevant_tx else None
        )
        
        # Shob response ready, return AnalyzeResponse
        return AnalyzeResponse(
            ticket_id=request.ticket_id,
            relevant_transaction_id=relevant_tx.transaction_id if relevant_tx else None,
            evidence_verdict=evidence_verdict,
            case_type=case_type,
            severity=severity,
            department=department,
            agent_summary=self._generate_summary(request, relevant_tx, case_type, evidence_verdict),
            recommended_next_action=self._generate_action(case_type, relevant_tx, evidence_verdict),
            customer_reply=customer_reply,
            human_review_required=self._requires_human_review(case_type, evidence_verdict, request),
            confidence=match_score,
            reason_codes=self._generate_reason_codes(case_type, evidence_verdict, relevant_tx)
        )
    
    def _parse_intent(self, complaint: str) -> Dict[str, Any]:
        """Parse complaint text to extract intent and key information"""
        complaint_lower = complaint.lower()
        intent = {
            'type': 'unknown',
            'amounts': [],
            'counterparties': [],
            'keywords': []
        }
        
       
        amount_pattern = r'(\d+[\.,]?\d*)\s*(?:taka|tk|bdt|৳)'
        amounts = re.findall(amount_pattern, complaint_lower)
        intent['amounts'] = [float(a.replace(',', '')) for a in amounts if a]
        
        
        if re.search(r'wrong|mistake|error|incorrect|not\s+meant', complaint_lower):
            intent['type'] = 'wrong_transfer'
        elif re.search(r'fail|not\s+working|error|issue|problem', complaint_lower):
            if re.search(r'pay|payment|recharge|bill', complaint_lower):
                intent['type'] = 'payment_failed'
        elif re.search(r'refund|money\s+back|return', complaint_lower):
            intent['type'] = 'refund_request'
        elif re.search(r'duplicate|twice|double|again|extra', complaint_lower):
            intent['type'] = 'duplicate_payment'
        elif re.search(r'settle|merchant|shop|seller', complaint_lower):
            intent['type'] = 'merchant_settlement_delay'
        elif re.search(r'agent|cash\s+in|deposit', complaint_lower):
            intent['type'] = 'agent_cash_in_issue'
        elif re.search(r'phish|scam|fake|fraud|otp|pin|password|suspicious|call.*asking', complaint_lower):
            intent['type'] = 'phishing_or_social_engineering'
        
        return intent
    
    def _find_relevant_transaction(self, complaint: str, 
                                   transactions: List[Transaction]) -> Tuple[Optional[Transaction], float]:
        """Find the transaction most relevant to the complaint"""
        if not transactions:
            return None, 0.0
        
        intent = self._parse_intent(complaint)
        best_match = None
        best_score = 0.0
        
        for tx in transactions:
            score = 0.0
            
            
            if intent['amounts']:
                for amount in intent['amounts']:
                    if abs(tx.amount - amount) < 1:
                        score += 0.4
                        break
            else:
                if tx.type in [TransactionType.TRANSFER, TransactionType.PAYMENT]:
                    score += 0.2
            
            
            if tx.status == TransactionStatus.COMPLETED:
                score += 0.2
            
            
            if intent['type'] == 'wrong_transfer' and tx.type == TransactionType.TRANSFER:
                score += 0.2
            elif intent['type'] == 'payment_failed' and tx.type == TransactionType.PAYMENT:
                score += 0.2
            elif intent['type'] == 'duplicate_payment' and tx.type == TransactionType.PAYMENT:
                score += 0.2
            elif intent['type'] == 'agent_cash_in_issue' and tx.type == TransactionType.CASH_IN:
                score += 0.2
            elif intent['type'] == 'merchant_settlement_delay' and tx.type == TransactionType.SETTLEMENT:
                score += 0.2
            
            if score > best_score:
                best_score = score
                best_match = tx
        
        if best_score < 0.3:
            return None, best_score
        
        return best_match, min(best_score, 1.0)
    
    def _determine_verdict(self, intent: Dict, relevant_tx: Optional[Transaction], 
                           match_score: float, transactions: List[Transaction]) -> EvidenceVerdict:
        """Determine if evidence supports, contradicts, or is insufficient"""
        
        if not relevant_tx:
            if intent['type'] == 'phishing_or_social_engineering':
                return EvidenceVerdict.INSUFFICIENT_DATA
            return EvidenceVerdict.INSUFFICIENT_DATA
        
        
        if intent['type'] == 'wrong_transfer':
            count = sum(1 for tx in transactions 
                       if tx.counterparty == relevant_tx.counterparty 
                       and tx.transaction_id != relevant_tx.transaction_id)
            if count >= 2:
                return EvidenceVerdict.INCONSISTENT
        
       
        if intent['type'] == 'duplicate_payment':
            duplicates = [tx for tx in transactions 
                         if tx.counterparty == relevant_tx.counterparty 
                         and tx.amount == relevant_tx.amount 
                         and tx.type == relevant_tx.type]
            if len(duplicates) >= 2:
                return EvidenceVerdict.CONSISTENT
        
        
        if intent['type'] == 'payment_failed' and relevant_tx:
            if relevant_tx.status == TransactionStatus.FAILED:
                return EvidenceVerdict.CONSISTENT
            elif relevant_tx.status == TransactionStatus.PENDING:
                return EvidenceVerdict.INSUFFICIENT_DATA
        
        if match_score >= 0.5:
            return EvidenceVerdict.CONSISTENT
        elif match_score >= 0.3:
            return EvidenceVerdict.INSUFFICIENT_DATA
        else:
            return EvidenceVerdict.INCONSISTENT
    
    def _classify_case(self, intent: Dict, relevant_tx: Optional[Transaction],
                       verdict: EvidenceVerdict, request: AnalyzeRequest) -> CaseType:
        """Determine the case type"""
        
       
        if intent['type'] == 'phishing_or_social_engineering':
            return CaseType.PHISHING_OR_SOCIAL_ENGINEERING
        
       
        if relevant_tx:
            if intent['type'] == 'wrong_transfer':
                return CaseType.WRONG_TRANSFER
            elif intent['type'] == 'payment_failed':
                return CaseType.PAYMENT_FAILED
            elif intent['type'] == 'refund_request':
                return CaseType.REFUND_REQUEST
            elif intent['type'] == 'duplicate_payment':
                return CaseType.DUPLICATE_PAYMENT
            elif intent['type'] == 'merchant_settlement_delay':
                return CaseType.MERCHANT_SETTLEMENT_DELAY
            elif intent['type'] == 'agent_cash_in_issue':
                return CaseType.AGENT_CASH_IN_ISSUE
        
        
        if request.user_type == UserType.MERCHANT and relevant_tx:
            if relevant_tx.type == TransactionType.SETTLEMENT:
                return CaseType.MERCHANT_SETTLEMENT_DELAY
        
       
        complaint_lower = request.complaint.lower()
        if re.search(r'wrong|mistake|error.*send|sent.*wrong', complaint_lower):
            return CaseType.WRONG_TRANSFER
        elif re.search(r'fail|deduct|charge|balance.*gone', complaint_lower):
            return CaseType.PAYMENT_FAILED
        elif re.search(r'refund|return.*money|money.*back', complaint_lower):
            return CaseType.REFUND_REQUEST
        elif re.search(r'duplicate|twice|double', complaint_lower):
            return CaseType.DUPLICATE_PAYMENT
        
        return CaseType.OTHER
    
    def _determine_severity(self, case_type: CaseType, verdict: EvidenceVerdict,
                            request: AnalyzeRequest) -> Severity:
        """Determine case severity with context"""
        
        base_severity = SEVERITY_MAPPING.get(case_type, Severity.LOW)
        
        
        if verdict == EvidenceVerdict.INCONSISTENT:
            if base_severity == Severity.LOW:
                return Severity.MEDIUM
            elif base_severity == Severity.MEDIUM:
                return Severity.HIGH
        
        
        if request.transaction_history:
            for tx in request.transaction_history:
                if tx.amount and tx.amount >= 10000:
                    if base_severity == Severity.LOW:
                        return Severity.MEDIUM
                    elif base_severity == Severity.MEDIUM:
                        return Severity.HIGH
        
        return base_severity
    
    def _generate_summary(self, request: AnalyzeRequest, relevant_tx: Optional[Transaction],
                          case_type: CaseType, verdict: EvidenceVerdict) -> str:
        """Generate agent summary"""
        
        tx_part = f" ({relevant_tx.transaction_id})" if relevant_tx else ""
        amount_part = f" {relevant_tx.amount} BDT" if relevant_tx and relevant_tx.amount else ""
        
        summaries = {
            CaseType.WRONG_TRANSFER: f"Customer reports sending{amount_part} via transaction{tx_part} which they now believe was sent to the wrong recipient.",
            CaseType.PAYMENT_FAILED: f"Customer reports a failed transaction{amount_part}{tx_part} but claims balance was deducted.",
            CaseType.REFUND_REQUEST: f"Customer requests refund of{amount_part} for transaction{tx_part}.",
            CaseType.DUPLICATE_PAYMENT: f"Customer reports duplicate payment{amount_part} for transaction{tx_part}.",
            CaseType.MERCHANT_SETTLEMENT_DELAY: f"Merchant reports settlement{amount_part}{tx_part} is delayed beyond expected timeframe.",
            CaseType.AGENT_CASH_IN_ISSUE: f"Customer reports cash-in{amount_part}{tx_part} not reflected in balance.",
            CaseType.PHISHING_OR_SOCIAL_ENGINEERING: "Customer reports suspicious communication asking for credentials.",
            CaseType.OTHER: f"Customer complaint: {request.complaint[:100]}..."
        }
        
        summary = summaries.get(case_type, f"Customer complaint regarding{amount_part}{tx_part}")
        
       
        if verdict == EvidenceVerdict.INCONSISTENT:
            summary += " Evidence does not fully support the claim."
        elif verdict == EvidenceVerdict.INSUFFICIENT_DATA:
            summary += " Insufficient data to verify the claim."
        
        return summary
    
    def _generate_action(self, case_type: CaseType, relevant_tx: Optional[Transaction],
                         verdict: EvidenceVerdict) -> str:
        """Generate recommended next action"""
        
        tx_part = f" {relevant_tx.transaction_id}" if relevant_tx else ""
        
        actions = {
            CaseType.WRONG_TRANSFER: f"Verify transaction{tx_part} details and initiate the wrong-transfer dispute workflow per policy.",
            CaseType.PAYMENT_FAILED: f"Investigate transaction{tx_part} ledger status. Initiate automatic reversal flow if balance was incorrectly deducted.",
            CaseType.REFUND_REQUEST: f"Inform customer that refund eligibility depends on merchant's policy. Guide them to contact the merchant directly.",
            CaseType.DUPLICATE_PAYMENT: f"Verify duplicate with payments_ops. Initiate reversal of duplicate transaction if confirmed.",
            CaseType.MERCHANT_SETTLEMENT_DELAY: f"Route to merchant_operations to verify settlement batch status and provide ETA.",
            CaseType.AGENT_CASH_IN_ISSUE: f"Investigate transaction{tx_part} pending status with agent operations.",
            CaseType.PHISHING_OR_SOCIAL_ENGINEERING: "Escalate to fraud_risk team immediately. Log the reported number for pattern analysis.",
            CaseType.OTHER: f"Review customer complaint and take appropriate action{tx_part}."
        }
        
        return actions.get(case_type, f"Review case{tx_part} and take appropriate action.")
    
    def _requires_human_review(self, case_type: CaseType, verdict: EvidenceVerdict,
                               request: AnalyzeRequest) -> bool:
        """Determine if human review is required"""
        
        
        if case_type in [CaseType.WRONG_TRANSFER, CaseType.PHISHING_OR_SOCIAL_ENGINEERING]:
            return True
        
        
        if verdict == EvidenceVerdict.INCONSISTENT:
            return True
        
       
        if request.transaction_history:
            for tx in request.transaction_history:
                if tx.amount and tx.amount >= 5000:
                    return True
        
        
        if request.user_type == UserType.MERCHANT:
            return True
        
        return False
    
    def _generate_reason_codes(self, case_type: CaseType, verdict: EvidenceVerdict,
                               relevant_tx: Optional[Transaction]) -> List[str]:
        """Generate reason codes"""
        
        codes = [case_type.value]
        
        if verdict == EvidenceVerdict.CONSISTENT:
            codes.append("evidence_consistent")
        elif verdict == EvidenceVerdict.INCONSISTENT:
            codes.append("evidence_inconsistent")
        else:
            codes.append("evidence_insufficient")
        
        if relevant_tx:
            codes.append("transaction_matched")
        
        return codes