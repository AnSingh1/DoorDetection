# Door Plan Detection

A modern, full-stack web application for detecting doors in architectural floor plans using YOLOv8.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **Poppler** (for PDF processing)

### Installing Poppler

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) and add to PATH.

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Door Plan Detection"
```

### 2. API Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import ultralytics; print('YOLOv8 ready!')"
```

### 3. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Optional: Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 4. Start the Application

**Terminal 1 - Backend Server:**
```bash
# From project root
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend Dev Server:**
```bash
cd frontend
npm run dev
```

### 5. Access the App

Open your browser and navigate to:
```
http://localhost:3000
```

The API backend will be running at `http://localhost:8000`

## Features

### Core Functionality
- **YOLOv8 Door Detection**: Advanced AI model trained for architectural floor plan analysis
- **Multiple Upload Methods**: 
  - Drag-and-drop interface
  - Click to browse files
  - **Paste from clipboard** (Ctrl/Cmd+V anywhere on the page)
- **Multi-Format Support**: Images (JPG, PNG, GIF) and PDF documents
- **Batch Processing**: Upload and process multiple files simultaneously

### Detection & Visualization
- **Accurate Bounding Boxes**: Precise door location with confidence scores
- **Interactive Results**: 
  - Fullscreen image viewer
  - Toggle annotations on/off
  - Side-by-side comparison (original vs. annotated)
- **Smart Preprocessing**: 
  - Binary threshold filtering (enhances line detection)
  - Adaptive image sizing (640px or 3200px based on input size)
  - Preserves aspect ratio without distortion

### User Experience
- **Modern UI**: Clean, professional interface with Tailwind CSS
- **Fully Responsive**: Optimized for desktop, tablet, and mobile
- **Real-time Notifications**: Success/error feedback with toast messages
- **File Management**: 
  - Preview uploaded files
  - Individual or bulk file removal
  - File metadata display (name, size, type)


## Tech Stack

### Frontend
- **Framework**: Next.js 16 (React 19)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React
- **Build Tool**: Next.js built-in

### Backend (API)
- **Framework**: FastAPI (Python 3.11+)
- **ML Model**: YOLOv8 (Ultralytics)
- **Deep Learning**: PyTorch 2.0+, TorchVision
- **Image Processing**: 
  - Pillow 10.0+ (image manipulation)
  - pdf2image 1.16+ (PDF to image conversion)
  - NumPy 1.24+ (array operations)
- **Server**: Uvicorn (ASGI server)

## Project Structure

```
Door Plan Detection/
├── api/
│   ├── main.py              # FastAPI application & endpoints
│   ├── detect.py            # YOLOv8 detection logic
│   ├── best.pt              # YOLOv8 trained model weights
│   └── __pycache__/
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main React component
│   │   ├── layout.tsx       # App layout wrapper
│   │   └── globals.css      # Global styles
│   ├── public/              # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.ts
├── requirements.txt         # Python dependencies
├── .venv/                   # Virtual environment (created locally)
└── README.md
```


## API Endpoints

### Health Check
```
GET /
```
Returns server health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "door-detection"
}
```

### Hello Endpoint
```
GET /api/hello
```
Simple greeting endpoint for testing.

**Response:**
```json
{
  "message": "Door Plan Detection API"
}
```

### Door Detection
```
POST /detect
```
Upload files (images/PDFs) for door detection.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `files` (one or more files)

**Response:**
```json
{
  "images": [
    {
      "filename": "floor-plan.pdf",
      "image": "data:image/png;base64,...",           // Annotated image
      "original_image": "data:image/png;base64,...",  // Original processed image
      "boxes": [
        {
          "x": 150,
          "y": 200,
          "width": 45,
          "height": 80,
          "className": "Door",
          "confidence": 0.92
        }
      ]
    }
  ]
}
```

**Error Responses:**
- `400`: No files provided
- `422`: File processing error (invalid format, corrupted file)
- `500`: Internal server error

## Configuration

### Environment Variables

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**API** (optional):
```env
# Currently using default values, but you can add:
# MODEL_PATH=./api/best.pt
# LOG_LEVEL=INFO
```

### Model Configuration

The detection model uses adaptive sizing:
- **Small images** (< 2000px): 640px inference size
- **Large images** (≥ 2000px): 3200px inference size

Binary threshold for preprocessing: **250** (optimized for floor plans)

## Development

### Running in Development Mode

**API with auto-reload:**
```bash
uvicorn api.main:app --reload --port 8000 --log-level debug
```

**Frontend with hot module replacement:**
```bash
cd frontend
npm run dev
```

### Testing the API

**Using cURL:**
```bash
curl -X POST http://localhost:8000/detect \
  -F "files=@/path/to/floor-plan.pdf" \
  -F "files=@/path/to/another-plan.png"
```

**Using Python:**
```python
import requests

files = [
    ('files', open('floor-plan.pdf', 'rb')),
    ('files', open('another-plan.png', 'rb'))
]

response = requests.post('http://localhost:8000/detect', files=files)
print(response.json())
```

### Code Style

**Python:**
- Follow PEP 8 guidelines
- Use type hints
- Docstrings for all functions

**TypeScript:**
- ESLint with Next.js config
- Strict TypeScript mode enabled
- Functional React components with hooks

## Building for Production

### Deploying to Vercel

This project is configured for easy deployment to Vercel:

1. **Push your code to GitHub**
2. **Import the project in Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import your GitHub repository
3. **Vercel will automatically**:
   - Detect the Next.js frontend in `/frontend`
   - Detect the Python API in `/api`
   - Deploy both as serverless functions

**Important Notes:**
- The `vercel.json` configuration routes API requests to `/api/*`
- Large ML models (>50MB) may need Vercel Pro for deployment
- Consider using a separate API deployment (Railway, Render, etc.) for the YOLOv8 model

### Frontend Build

```bash
cd frontend
npm run build
npm start  # Runs production server on port 3000
```

### API Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn (production ASGI server)
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (Optional)

Create `Dockerfile` for containerized deployment:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ ./api/
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


## Troubleshooting

### Common Issues

**"Model not found" or detection not working:**
- Ensure `best.pt` exists in the `api/` directory
- Verify YOLOv8 is properly installed: `python -c "from ultralytics import YOLO; print('OK')"`
- Check model file is not corrupted

**PDF processing fails:**
- Verify Poppler is installed: `pdftoppm -v`
- On macOS: `brew install poppler`
- On Windows: Ensure Poppler bin directory is in PATH

**CORS errors in browser:**
- API includes permissive CORS for development (`allow_origins=["*"]`)
- For production, update `api/main.py` to specify allowed origins
- Example: `allow_origins=["https://yourdomain.com"]`

**Port already in use:**
- API: Change port with `--port 8001`
- Frontend: Set in `package.json` or use `PORT=3001 npm run dev`

**Dependencies not installing:**
- Python: Ensure Python 3.11+ (`python --version`)
- Node: Ensure Node 18+ (`node --version`)
- Try upgrading pip: `pip install --upgrade pip`

**Image not displaying in results:**
- Check browser console for errors
- Verify API response contains base64-encoded images
- Ensure sufficient memory for large images

**Slow detection:**
- Large images take longer (3200px inference)
- Try reducing image resolution before upload
- Consider GPU acceleration for PyTorch (CUDA)

### Enable GPU Acceleration

For faster detection with NVIDIA GPU:

```bash
# Uninstall CPU-only PyTorch
pip uninstall torch torchvision

# Install GPU version (CUDA 11.8)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Verify GPU is detected
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## 📝 Technical Details

### Detection Pipeline

1. **File Upload**: Multi-file support (drag-drop, browse, paste)
2. **Format Conversion**: PDFs → PNG (150 DPI)
3. **Preprocessing**:
   - Convert to grayscale
   - Apply binary threshold (>250 = white)
   - Convert back to RGB for model
4. **Adaptive Sizing**:
   - Images < 2000px → 640px inference
   - Images ≥ 2000px → 3200px inference
5. **YOLOv8 Inference**: Detect doors with confidence scores
6. **Post-processing**:
   - Filter by "door" class
   - Extract bounding boxes and confidence
   - Annotate image with boxes and labels
7. **Response**: Return annotated + original images + box coordinates

### Model Information

- **Architecture**: YOLOv8 (You Only Look Once v8)
- **Training**: Custom-trained on architectural floor plans
- **Classes**: Door (single class detection)
- **Input Format**: RGB images
- **Output**: Bounding boxes (x, y, width, height) + confidence scores

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **YOLOv8** by Ultralytics for the detection framework
- **FastAPI** for the high-performance backend
- **Next.js** team for the modern React framework
- **Tailwind CSS** for the utility-first styling

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

---

**Made with ❤️ by Anmol**
