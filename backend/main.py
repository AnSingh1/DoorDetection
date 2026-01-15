"""FastAPI backend for Door Plan Detection."""

import base64
import io
import logging
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .detect import detect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Door Plan Detection API",
    description="API for detecting doors in architectural floor plans",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "door-detection"}


@app.get("/api/hello")
def hello():
    """Simple greeting endpoint."""
    return {"message": "Door Plan Detection API"}

@app.post("/detect")
async def detect_endpoint(files: List[UploadFile] = File(...)):
    """Process files and return door detection results."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    
    for file in files:
        try:
            content = await file.read()
            annotated, original, boxes = detect(content, file.filename or "unknown")
            
            # Encode images
            ann_buf = io.BytesIO()
            annotated.save(ann_buf, format="PNG")
            ann_b64 = base64.b64encode(ann_buf.getvalue()).decode()
            
            orig_buf = io.BytesIO()
            original.save(orig_buf, format="PNG")
            orig_b64 = base64.b64encode(orig_buf.getvalue()).decode()
            
            results.append({
                "filename": file.filename,
                "image": f"data:image/png;base64,{ann_b64}",
                "original_image": f"data:image/png;base64,{orig_b64}",
                "boxes": boxes,
            })
        except ValueError as e:
            logger.error(f"Processing error: {e}")
            raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal error") from e
    
    return {"images": results}

