# 📝 Complete GitHub README for QueueStorm Investigator Submission


---

```markdown
# QueueStorm Investigator

> AI/API SupportOps Challenge for Digital Finance  
> SUST CSE Carnival 2026 · Codex Community Hackathon

[![Live API](https://queuestorm-investigator-2.onrender.com)
[![Python](https://python.org)
[![FastAPI](https://fastapi.tiangolo.com)
[![License](LICENSE)

---

## 📋 Overview

QueueStorm Investigator is an AI-powered support copilot that analyzes customer complaints against transaction history. It classifies cases, determines severity, routes to appropriate departments, and generates safe customer replies—all while enforcing strict fintech safety rules.

### The Problem

During large campaigns, support teams face overwhelming complaint volumes. Agents need help investigating:
- Wrong transfers
- Failed payments with balance deductions
- Duplicate payments
- Merchant settlement delays
- Agent cash-in issues
- Phishing and social engineering attempts

### The Solution

This API service:
1. **Investigates** complaints against transaction history
2. **Classifies** cases into 8+ categories
3. **Routes** to the correct department
4. **Generates** safe customer replies
5. **Escalates** suspicious or high-value cases

---

## 🚀 Live API

| Service | URL |
|---------|-----|
| **Live API** | [https://queuestorm-investigator-2.onrender.com] |
| **Health Check** | [https://queuestorm-investigator-2.onrender.com/health] |

### Quick Test

```bash
# Health check
curl https://queuestorm-investigator-2.onrender.com/health

# Analyze a ticket
curl -X POST https://queuestorm-investigator-2.onrender.com/analyze-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TKT-001",
    "complaint": "I sent 5000 taka to a wrong number",
    "transaction_history": [
      {
        "transaction_id": "TXN-9101",
        "timestamp": "2026-04-14T14:08:22Z",
        "type": "transfer",
        "amount": 5000,
        "counterparty": "+8801719876543",
        "status": "completed"
      }
    ]
  }'
```

---

## 📊 API Endpoints

### GET /health
Returns service health status.

**Response:**
```json
{"status": "ok"}
```

### POST /analyze-ticket
Analyzes a support ticket and returns investigation results.

**Request:**
```json
{
  "ticket_id": "TKT-001",
  "complaint": "I sent 5000 taka to a wrong number",
  "language": "en",
  "channel": "in_app_chat",
  "user_type": "customer",
  "campaign_context": "boishakh_bonanza_day_1",
  "transaction_history": [
    {
      "transaction_id": "TXN-9101",
      "timestamp": "2026-04-14T14:08:22Z",
      "type": "transfer",
      "amount": 5000,
      "counterparty": "+8801719876543",
      "status": "completed"
    }
  ]
}
```

**Response:**
```json
{
  "ticket_id": "TKT-001",
  "relevant_transaction_id": "TXN-9101",
  "evidence_verdict": "consistent",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports sending 5000.0 BDT via transaction (TXN-9101) which they now believe was sent to the wrong recipient.",
  "recommended_next_action": "Verify transaction TXN-9101 details and initiate the wrong-transfer dispute workflow per policy.",
  "customer_reply": "We have noted your concern about transaction TXN-9101. Please do not share your PIN or OTP with anyone. Our dispute team will review the case and contact you through official support channels.",
  "human_review_required": true,
  "confidence": 0.8,
  "reason_codes": ["wrong_transfer", "evidence_consistent", "transaction_matched"]
}
```

---

## 🔍 Case Classification

### Supported Case Types

| Case Type | Department | Severity |
|-----------|------------|----------|
| `wrong_transfer` | Dispute Resolution | High |
| `payment_failed` | Payments Ops | High |
| `refund_request` | Customer Support | Low |
| `duplicate_payment` | Payments Ops | High |
| `merchant_settlement_delay` | Merchant Operations | Medium |
| `agent_cash_in_issue` | Agent Operations | High |
| `phishing_or_social_engineering` | Fraud Risk | Critical |
| `other` | Customer Support | Low |

### Evidence Verdicts

| Verdict | Meaning |
|---------|---------|
| `consistent` | Evidence supports the complaint |
| `inconsistent` | Evidence contradicts the complaint |
| `insufficient_data` | Cannot determine from provided history |

---

## 🛡️ Safety Rules

The system enforces strict safety rules:

| Rule | Enforcement |
|------|-------------|
| ❌ Never asks for PIN, OTP, or password | Automated detection |
| ❌ Never promises refunds or reversals without authority | Automated detection |
| ❌ Never directs customers to suspicious third parties | Automated detection |
| ✅ Always warns customers to protect credentials | Built into every reply |

### Example Safe Reply

> "We have noted your concern about transaction TXN-9101. Please do not share your PIN or OTP with anyone. Our dispute team will review the case and contact you through official support channels."

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  GET /health          →  {"status": "ok"}                 │
│  POST /analyze-ticket →  Structured JSON Response          │
├─────────────────────────────────────────────────────────────┤
│                    Core Logic Pipeline                      │
│  1. Parse complaint intent (regex pattern matching)        │
│  2. Find relevant transaction (scoring algorithm)          │
│  3. Determine evidence verdict                             │
│  4. Classify case type                                     │
│  5. Assign severity and department                         │
│  6. Generate safe customer reply                           │
│  7. Flag for human review if needed                        │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI 0.104.1 |
| **Validation** | Pydantic 2.4.2 |
| **Server** | Uvicorn 0.24.0 |
| **AI/ML** | Rule-based logic (no external APIs) |
| **Deployment** | Render.com |
| **Container** | Docker |

### AI/Model Approach

**Model Used:** None (Rule-based system)

**Why Rule-based:**
- ✅ Deterministic and predictable
- ✅ Zero API costs
- ✅ No external dependencies
- ✅ Fast response times
- ✅ Safe for production use

**Pattern Matching Includes:**
- Amount extraction
- Transaction type matching
- Counterparty relationship detection

---

## 🚀 Local Development

### Prerequisites
- Python 3.11.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/queuestorm-investigator.git
cd queuestorm-investigator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Analyze a ticket
curl -X POST http://localhost:8000/analyze-ticket \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```



## 📁 Project Structure

```
queuestorm-investigator/
├── app/
│   ├── __init__.py          # Package marker
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # Pydantic schemas
│   ├── investigator.py      # Core investigation logic
│   ├── safety.py            # Safety guardrails
│   ├── constants.py         # Enums and mappings
│   └── config.py            # Configuration
├── requirements.txt         # Python dependencies
├── render.yaml              # Render deployment config
├── .env.example             # Environment variables
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8000` |
| `ENVIRONMENT` | Runtime environment | `production` |



## 🧪 Testing

### Sample Test Cases

| Test Case | Expected Result |
|-----------|-----------------|
| Wrong transfer with matching evidence | `wrong_transfer`, `consistent` |
| Wrong transfer with inconsistent evidence | `wrong_transfer`, `inconsistent` |
| Payment failed | `payment_failed`, `payments_ops` |
| Refund request (safe handling) | `refund_request`, no refund promise |
| Duplicate payment | `duplicate_payment` |
| Merchant settlement delay | `merchant_settlement_delay` |
| Agent cash-in issue | `agent_cash_in_issue` |
| Phishing report | `phishing_or_social_engineering`, `critical` |
| Bangla complaint | Supports Bangla language |
| Empty transaction history | `insufficient_data` |



## 👥 Team

Black_Caps

---

## 🎯 Live Demo

Try the live API: [https://queuestorm-investigator-2.onrender.com](https://queuestorm-investigator-2.onrender.com)

### Quick Example

```bash
curl -X POST https://queuestorm-investigator-2.onrender.com/analyze-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TKT-DEMO-001",
    "complaint": "I sent 5000 taka to a wrong number",
    "transaction_history": [
      {
        "transaction_id": "TXN-DEMO-001",
        "timestamp": "2026-06-26T10:00:00Z",
        "type": "transfer",
        "amount": 5000,
        "counterparty": "+8801719876543",
        "status": "completed"
      }
    ]
  }'
```



```

---






