"""
Lark PDF Signature Backend
FastAPI server for PDF signing with Lark Base/Sheet integration
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import os
import logging
from pathlib import Path

# Import handlers (to be created)
# from handlers.pdf_handler import fetch_pdf, save_pdf
# from handlers.sign_handler import sign_pdf_with_signature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Lark PDF Signature", version="0.1.0")

# Mount frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def root():
    return {"message": "Lark PDF Signature Service", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

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
            return JSONResponse({
                "html": """<!DOCTYPE html>
<html>
<head><title>PDF Signing</title></head>
<body>
<h1>PDF Signature Service</h1>
<p>Signing page for record_id: {record_id}, file_id: {file_id}</p>
<p>(Frontend page will be loaded here)</p>
</body>
</html>""".format(record_id=record_id, file_id=file_id)
            })
    except Exception as e:
        logger.error(f"Error loading signing page: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sign")
async def sign_pdf(record_id: str = Query(...), file_id: str = Query(...)):
    """
    API endpoint for PDF signing
    
    Receives signature data and returns signed PDF
    
    TODO: Implement signing logic
    """
    return {"status": "pending", "message": "Signing endpoint - implementation pending"}

@app.on_event("startup")
async def startup_event():
    logger.info("Lark PDF Signature Service starting...")
    # TODO: Initialize Lark API client, verify credentials
    logger.info("Service ready")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Service shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
