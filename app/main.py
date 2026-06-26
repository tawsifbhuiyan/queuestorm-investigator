from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import uvicorn
import os
from dotenv import load_dotenv

from app.models import AnalyzeRequest, AnalyzeResponse
from app.investigator import QueueStormInvestigator
from app.safety import SafetyChecker

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="QueueStorm Investigator",
    description="AI/API SupportOps Challenge for Digital Finance - SUST CSE Carnival 2026",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


investigator = QueueStormInvestigator()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "QueueStorm Investigator",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "analyze": "POST /analyze-ticket"
        },
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - required for judge harness"""
    return {"status": "ok"}

@app.post("/analyze-ticket", 
          response_model=AnalyzeResponse,
          status_code=status.HTTP_200_OK)
async def analyze_ticket(request: AnalyzeRequest):
    """
    Analyze a support ticket and return investigation results
    
    Required for judge harness testing
    """
    try:
        
        response = investigator.investigate(request)
        
       
        is_safe, violations = SafetyChecker.check_safety(response.customer_reply)
        if not is_safe:
          
            pass
        
        return response
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Validation error", "details": str(e)}
        )
    except Exception as e:
       
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal processing error"}
        )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid request payload", "errors": str(exc)}
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )