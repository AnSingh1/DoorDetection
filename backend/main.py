from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import io
import base64
from PIL import Image, ImageDraw
from typing import List
import json

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
async def detect(files: List[UploadFile] = File(...)):
    """
    Process uploaded files and return one image per file.
    Each image contains the filename and file information.
    """
    try:
        if not files:
            return {"error": "No files provided"}
        
        images_data = []
        
        # Create one image per file
        for i, file in enumerate(files):
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Add text with file information
            draw.text((50, 50), "Door Plan Detection Result", fill='black')
            draw.text((50, 100), f"File {i+1} of {len(files)}", fill='black')
            draw.text((50, 150), f"Filename: {file.filename}", fill='black')
            draw.text((50, 200), f"Content-Type: {file.content_type}", fill='black')
            
            # Add some sample detection info
            draw.text((50, 300), "Detection Status: Complete", fill='green')
            draw.text((50, 350), "Confidence: 95.2%", fill='green')
            
            # Convert image to base64
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            base64_image = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
            
            images_data.append({
                "filename": file.filename,
                "image": f"data:image/png;base64,{base64_image}"
            })
        
        return {"images": images_data}
    except Exception as e:
        return {"error": str(e)}

