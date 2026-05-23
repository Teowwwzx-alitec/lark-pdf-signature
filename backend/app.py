"""
Lark PDF Signature Backend
FastAPI server for PDF signing with Lark Base/Sheet integration
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Import handlers
from lark_client import get_lark_client, LarkClient
from pdf_handler import get_pdf_handler
from sign_handler import get_signing_handler

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lark PDF Signature",
    version="0.1.0",
    description="PDF signing solution for Lark Base & Sheet records"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# ============================================================================
# Models
# ============================================================================

class SignatureRequest(BaseModel):
    """Signature submission from frontend"""
    record_id: str
    file_id: str
    table_id: Optional[str] = None
    timestamp: str
    position: dict  # {x, y, width, height}

# ============================================================================
# Routes
# ============================================================================

@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "Lark PDF Signature",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "signing_ui": "/sign?record_id=xxx&file_id=yyy",
            "api": "/api/sign"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Verify Lark connection by getting a token
        lark_client = get_lark_client()
        lark_client.get_tenant_token()
        return {"status": "healthy", "lark": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 500

@app.get("/sign")
async def get_signing_page(record_id: str = Query(...), file_id: str = Query(...)):
    """
    Serve the signing UI page
    
    Query params:
    - record_id: Lark Base record ID
    - file_id: File ID of the PDF attachment
    """
    try:
        frontend_file = Path(__file__).parent.parent / "frontend" / "index.html"
        
        if frontend_file.exists():
            return FileResponse(str(frontend_file))
        else:
            raise FileNotFoundError("Frontend page not found")
    except Exception as e:
        logger.error(f"Error loading signing page: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sign")
async def sign_pdf(
    record_id: str = Query(...),
    file_id: str = Query(...),
    signature: SignatureRequest = None  # Will receive JSON body instead
):
    """
    API endpoint for PDF signing
    
    Receives signature data, signs the PDF, and uploads back to Lark
    """
    try:
        logger.info(f"Signing request: record_id={record_id}, file_id={file_id}")
        
        # Get handlers
        pdf_handler = get_pdf_handler()
        signing_handler = get_signing_handler()
        lark_client = get_lark_client()
        
        # Fetch original PDF
        pdf_content, cache_path = pdf_handler.fetch_pdf(file_id)
        logger.info(f"Fetched PDF: {len(pdf_content)} bytes")
        
        # Extract signature position from request
        # In real implementation, this comes from request body
        # For now, using defaults for testing
        signature_x = 100
        signature_y = 100
        signature_width = 150
        signature_height = 100
        timestamp = "2026-05-23 15:55:00"  # TODO: Get from request
        
        # Sign the PDF
        signed_pdf_content = signing_handler.sign_pdf(
            pdf_content=pdf_content,
            signature_x=signature_x,
            signature_y=signature_y,
            signature_width=signature_width,
            signature_height=signature_height,
            timestamp=timestamp
        )
        
        logger.info(f"PDF signed: {len(signed_pdf_content)} bytes")
        
        # Upload signed PDF back to Lark
        # TODO: Implement upload and record update
        # For now, just return success
        
        return {
            "status": "success",
            "message": "PDF signed successfully",
            "signed_pdf_size": len(signed_pdf_content),
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"Error signing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Startup event - initialize connections"""
    logger.info("=" * 50)
    logger.info("Lark PDF Signature Service Starting")
    logger.info("=" * 50)
    
    try:
        # Test Lark connection
        lark_client = get_lark_client()
        token = lark_client.get_tenant_token()
        logger.info(f"✓ Lark API connected (token: {token[:10]}...)")
        
        # Initialize handlers
        pdf_handler = get_pdf_handler()
        logger.info(f"✓ PDF handler initialized (cache: {pdf_handler.cache_dir})")
        
        signing_handler = get_signing_handler()
        logger.info("✓ Signing handler initialized")
        
        logger.info("=" * 50)
        logger.info("Service ready!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("Service shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
