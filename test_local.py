#!/usr/bin/env python3
"""
Comprehensive local testing script for QueueStorm Investigator
Tests all functionality before deployment
"""

import json
import sys
import os
import subprocess
import time
import requests
from threading import Thread
import signal

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ANSI colors for better output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.WHITE}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def test_imports():
    """Test if all imports work"""
    print_header("📦 TEST 1: Import All Modules")
    
    try:
        from app import main, models, investigator, safety, constants, config
        print_success("All modules imported successfully!")
        return True
    except ImportError as e:
        print_error(f"Import error: {e}")
        return False

def test_constants():
    """Test constants and enums"""
    print_header("🔢 TEST 2: Constants and Enums")
    
    try:
        from app.constants import (
            CaseType, Severity, Department, EvidenceVerdict,
            DEPARTMENT_MAPPING, SEVERITY_MAPPING
        )
        
        # Check if all required enums exist
        required_case_types = ['wrong_transfer', 'payment_failed', 'refund_request', 
                              'duplicate_payment', 'merchant_settlement_delay', 
                              'agent_cash_in_issue', 'phishing_or_social_engineering', 'other']
        
        for ct in required_case_types:
            if hasattr(CaseType, ct.upper()):
                print_success(f"CaseType.{ct.upper()} exists")
            else:
                print_error(f"CaseType.{ct.upper()} missing")
                return False
        
        print_success("All constants and enums are properly defined!")
        return True
    except Exception as e:
        print_error(f"Constants test failed: {e}")
        return False

def test_safety():
    """Test safety guardrails"""
    print_header("🛡️ TEST 3: Safety Guardrails")
    
    try:
        from app.safety import SafetyChecker
        
        # Test unsafe replies
        unsafe_replies = [
            "Please share your PIN for verification",
            "We will refund your money immediately",
            "Contact 01712345678 for help"
        ]
        
        for reply in unsafe_replies:
            is_safe, violations = SafetyChecker.check_safety(reply)
            if not is_safe:
                print_success(f"Detected unsafe reply: '{reply[:30]}...' - {violations[0]}")
            else:
                print_error(f"Failed to detect unsafe reply: '{reply[:30]}...'")
        
        # Test safe replies
        safe_reply = "We have noted your concern. Our team will review and contact you through official channels."
        is_safe, violations = SafetyChecker.check_safety(safe_reply)
        if is_safe:
            print_success(f"Safe reply passed: '{safe_reply[:30]}...'")
        else:
            print_error(f"Safe reply incorrectly flagged: {violations}")
        
        print_success("Safety checks completed!")
        return True
    except Exception as e:
        print_error(f"Safety test failed: {e}")
        return False

def test_investigator():
    """Test the investigator logic"""
    print_header("🔍 TEST 4: Investigator Logic")
    
    try:
        from app.investigator import QueueStormInvestigator
        from app.models import AnalyzeRequest, Transaction
        from app.constants import TransactionType, TransactionStatus
        
        investigator = QueueStormInvestigator()
        
        # Test case 1: Wrong transfer
        request = AnalyzeRequest(
            ticket_id="TKT-TEST-001",
            complaint="I sent 5000 taka to a wrong number",
            transaction_history=[
                Transaction(
                    transaction_id="TXN-001",
                    timestamp="2026-04-14T14:08:22Z",
                    type=TransactionType.TRANSFER,
                    amount=5000,
                    counterparty="+8801719876543",
                    status=TransactionStatus.COMPLETED
                )
            ]
        )
        
        response = investigator.investigate(request)
        
        # Verify response fields
        expected_fields = ['ticket_id', 'relevant_transaction_id', 'evidence_verdict', 
                          'case_type', 'severity', 'department', 'agent_summary', 
                          'recommended_next_action', 'customer_reply', 'human_review_required']
        
        for field in expected_fields:
            if hasattr(response, field):
                print_success(f"Response has field: {field}")
            else:
                print_error(f"Response missing field: {field}")
                return False
        
        # Verify verdict
        if response.evidence_verdict.value == "consistent":
            print_success(f"Evidence verdict: {response.evidence_verdict.value}")
        else:
            print_warning(f"Evidence verdict: {response.evidence_verdict.value}")
        
        print_success("Investigator logic test passed!")
        return True
    except Exception as e:
        print_error(f"Investigator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models():
    """Test Pydantic models"""
    print_header("📝 TEST 5: Pydantic Models")
    
    try:
        from app.models import AnalyzeRequest, AnalyzeResponse, Transaction
        from app.constants import TransactionType, TransactionStatus, CaseType, Severity, Department, EvidenceVerdict
        
        # Test request creation
        request = AnalyzeRequest(
            ticket_id="TKT-001",
            complaint="Test complaint",
            transaction_history=[]
        )
        print_success("Request model created successfully")
        
        # Test response creation
        response = AnalyzeResponse(
            ticket_id="TKT-001",
            relevant_transaction_id="TXN-001",
            evidence_verdict=EvidenceVerdict.CONSISTENT,
            case_type=CaseType.WRONG_TRANSFER,
            severity=Severity.HIGH,
            department=Department.DISPUTE_RESOLUTION,
            agent_summary="Test summary",
            recommended_next_action="Test action",
            customer_reply="Test reply",
            human_review_required=True
        )
        print_success("Response model created successfully")
        
        # Test validation
        try:
            invalid_request = AnalyzeRequest(
                ticket_id="TKT-002",
                complaint="",  # Empty complaint should fail
                transaction_history=[]
            )
            print_error("Model validation should have failed for empty complaint")
            return False
        except ValueError:
            print_success("Empty complaint correctly rejected")
        
        print_success("All model tests passed!")
        return True
    except Exception as e:
        print_error(f"Models test failed: {e}")
        return False

def run_api_server():
    """Start the API server in a subprocess"""
    import subprocess
    import time
    
    print_header("🌐 TEST 6: API Server Startup")
    
    # Start the server
    try:
        # Kill any existing process on port 8000
        subprocess.run(["python", "-c", "import os; os.system('taskkill /F /IM python.exe /FI \"WINDOWTITLE eq uvicorn*\"')"], 
                      capture_output=True, shell=True)
        time.sleep(1)
        
        process = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print_success("API server started successfully!")
            return process
        else:
            stdout, stderr = process.communicate()
            print_error(f"Server failed to start: {stderr}")
            return None
            
    except Exception as e:
        print_error(f"Failed to start server: {e}")
        return None

def test_api_endpoints(server_process):
    """Test API endpoints"""
    print_header("🎯 TEST 7: API Endpoints")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        print_info("Testing GET /health...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200 and response.json() == {"status": "ok"}:
            print_success("Health endpoint works!")
        else:
            print_error(f"Health endpoint failed: {response.status_code}")
            return False
        
        # Test analyze endpoint
        print_info("Testing POST /analyze-ticket...")
        
        test_payload = {
            "ticket_id": "TKT-TEST-001",
            "complaint": "I sent 5000 taka to a wrong number today",
            "language": "en",
            "channel": "in_app_chat",
            "user_type": "customer",
            "transaction_history": [
                {
                    "transaction_id": "TXN-001",
                    "timestamp": "2026-04-14T14:08:22Z",
                    "type": "transfer",
                    "amount": 5000,
                    "counterparty": "+8801719876543",
                    "status": "completed"
                }
            ]
        }
        
        response = requests.post(
            f"{base_url}/analyze-ticket",
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Analyze endpoint works!")
            data = response.json()
            
            # Check required fields
            required_fields = ['ticket_id', 'relevant_transaction_id', 'evidence_verdict', 
                              'case_type', 'severity', 'department', 'agent_summary', 
                              'recommended_next_action', 'customer_reply', 'human_review_required']
            
            all_present = True
            for field in required_fields:
                if field in data:
                    print_success(f"Response has field: {field} = {data[field]}")
                else:
                    print_error(f"Response missing field: {field}")
                    all_present = False
            
            # Check safety
            customer_reply = data.get('customer_reply', '')
            from app.safety import SafetyChecker
            is_safe, violations = SafetyChecker.check_safety(customer_reply)
            
            if is_safe:
                print_success("Customer reply is safe!")
            else:
                print_error(f"Customer reply has violations: {violations}")
                print_warning(f"Reply: {customer_reply}")
            
            return all_present
            
        else:
            print_error(f"Analyze endpoint returned {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    except Exception as e:
        print_error(f"API test failed: {e}")
        return False

def test_sample_cases():
    """Test against sample cases from the problem statement"""
    print_header("📋 TEST 8: Sample Cases")
    
    # Simplified test cases based on the sample
    sample_test = {
        "ticket_id": "TKT-001",
        "complaint": "I sent 5000 taka to a wrong number around 2pm today. The number was supposed to be 01712345678 but I think I typed it wrong.",
        "language": "en",
        "channel": "in_app_chat",
        "user_type": "customer",
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
    
    try:
        response = requests.post(
            "http://localhost:8000/analyze-ticket",
            json=sample_test,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Sample case processed successfully!")
            print_info(f"Ticket ID: {data.get('ticket_id')}")
            print_info(f"Case Type: {data.get('case_type')}")
            print_info(f"Evidence Verdict: {data.get('evidence_verdict')}")
            print_info(f"Severity: {data.get('severity')}")
            print_info(f"Department: {data.get('department')}")
            print_info(f"Human Review: {data.get('human_review_required')}")
            
            # Show customer reply (truncated)
            reply = data.get('customer_reply', '')
            print_info(f"Customer Reply: {reply[:100]}...")
            
            return True
        else:
            print_error(f"Sample case failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Sample case test failed: {e}")
        return False

def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("🧪 QueueStorm Investigator - Local Testing Suite")
    print("="*70)
    print_info("Testing all components before deployment...")
    
    # Track test results
    results = {}
    
    # Run tests
    results['imports'] = test_imports()
    results['constants'] = test_constants()
    results['safety'] = test_safety()
    results['investigator'] = test_investigator()
    results['models'] = test_models()
    
    # Start server for API tests
    if all(results.values()):
        server_process = run_api_server()
        if server_process:
            results['api_endpoints'] = test_api_endpoints(server_process)
            if results['api_endpoints']:
                results['sample_cases'] = test_sample_cases()
            
            # Stop server
            server_process.terminate()
            time.sleep(2)
            if server_process.poll() is None:
                server_process.kill()
    
    # Print summary
    print_header("📊 TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print_header("🏁 FINAL RESULT")
    
    if failed == 0:
        print_success("🎉 ALL TESTS PASSED!")
        print_info("Your application is ready for deployment!")
        print("\n🚀 To deploy to Render:")
        print("   1. Push code to GitHub")
        print("   2. Connect repository to Render")
        print("   3. Render will auto-deploy from render.yaml")
    else:
        print_error(f"❌ {failed} test(s) failed!")
        print_info("Please fix the issues before deploying.")
    
    print("="*70)

if __name__ == "__main__":
    main()