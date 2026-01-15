from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import io
from PIL import Image, ImageDraw
from typing import List
import tempfile
import os

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
    Process uploaded files and return a processed image.
    For now, this creates a simple image with file information.
    """
    try:
        if not files:
            return {"error": "No files provided"}
        
        # Create a new image to return
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text with file information
        draw.text((50, 50), "Door Plan Detection Results", fill='black')
        draw.text((50, 100), f"Files processed: {len(files)}", fill='black')
        
        y_offset = 150
        for i, file in enumerate(files):
            draw.text((50, y_offset), f"{i+1}. {file.filename}", fill='black')
            y_offset += 40
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_file.name, format='PNG')
        temp_file.close()
        
        return FileResponse(temp_file.name, media_type="image/png", filename="detection_result.png")
    except Exception as e:
        return {"error": str(e)}

