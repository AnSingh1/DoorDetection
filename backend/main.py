from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import io
import base64
from typing import List
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from detect import detect

app = FastAPI()

# Add CORS middleware FIRST - it must be the first middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello World from the Dashboard"}

@app.post("/detect")
async def detect_endpoint(files: List[UploadFile] = File(...)):
    """
    Process uploaded files using the detect function and return detection results.
    """
    try:
        if not files:
            return {"error": "No files provided"}
        
        images_data = []
        
        # Process each file with the detect function
        for file in files:
            # Read file content
            file_content = await file.read()
            
            # Run detection - returns (annotated_img, original_img, boxes_data)
            annotated_img, original_img, boxes_data = detect(file_content, file.filename)
            
            # Convert annotated image to base64
            img_bytes = io.BytesIO()
            annotated_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            base64_annotated = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
            
            # Convert original image to base64
            img_bytes = io.BytesIO()
            original_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            base64_original = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
            
            images_data.append({
                "filename": file.filename,
                "image": f"data:image/png;base64,{base64_annotated}",
                "original_image": f"data:image/png;base64,{base64_original}",
                "boxes": boxes_data
            })
        
        return {"images": images_data}
    except Exception as e:
        return {"error": str(e)}

