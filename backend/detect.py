"""Door detection module using YOLOv8."""

import io
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from pdf2image import convert_from_bytes
from PIL import Image

logger = logging.getLogger(__name__)

# Attempt to import ultralytics
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    YOLO = None  # type: ignore
    logger.warning("ultralytics not installed. Detection disabled.")

# Constants
MODEL_PATH = Path(__file__).parent / "best.pt"
DEFAULT_DPI = 150
LARGE_IMAGE_THRESHOLD = 2000
LARGE_IMAGE_SIZE = 3200
DEFAULT_IMAGE_SIZE = 640
BINARY_THRESHOLD = 250

# Lazy-loaded model singleton
_model = None


def get_model():
    """Lazy-load the YOLO model."""
    global _model
    if _model is None and ULTRALYTICS_AVAILABLE and MODEL_PATH.exists():
        try:
            _model = YOLO(str(MODEL_PATH))
            logger.info(f"Loaded model from {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Could not load model: {e}")
    return _model

def _load_image(file_content: bytes, filename: str) -> Image.Image:
    """Load image from bytes, handling PDFs and image files."""
    if filename.lower().endswith('.pdf'):
        images = convert_from_bytes(file_content, dpi=DEFAULT_DPI)
        return images[0]
    return Image.open(io.BytesIO(file_content))


def _preprocess_image(img: Image.Image) -> Image.Image:
    """Apply binary threshold to enhance lines for detection."""
    gray = np.array(img.convert('L'))
    binary_mask = (gray > BINARY_THRESHOLD).astype(np.uint8)
    img_data = binary_mask * 255
    return Image.fromarray(img_data).convert('RGB')


def _extract_door_boxes(result) -> List[Dict]:
    """Extract door bounding boxes from YOLO result."""
    boxes_data = []
    
    if result.boxes is None or len(result.boxes) == 0:
        return boxes_data
    
    class_names = result.names
    door_class_id = next(
        (cid for cid, name in class_names.items() if name.lower() == 'door'),
        None
    )
    
    if door_class_id is None:
        logger.warning(f"'door' class not found. Available: {list(class_names.values())}")
        return boxes_data
    
    door_mask = result.boxes.cls == door_class_id
    if not door_mask.any():
        return boxes_data
    
    filtered_boxes = result.boxes[door_mask]
    result.boxes = filtered_boxes
    
    for box in filtered_boxes:
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
        boxes_data.append({
            "x": x1,
            "y": y1,
            "width": x2 - x1,
            "height": y2 - y1,
            "className": "Door",
            "confidence": float(box.conf[0].cpu().numpy())
        })
    
    return boxes_data


def detect(file_content: bytes, filename: str) -> Tuple[Image.Image, Image.Image, List[Dict]]:
    """Process a file and run YOLOv8 door detection.
    
    Args:
        file_content: Raw file bytes.
        filename: Filename to determine type.
    
    Returns:
        Tuple of (annotated_image, processed_image, boxes_data).
    
    Raises:
        ValueError: If file cannot be processed.
    """
    try:
        raw_img = _load_image(file_content, filename)
        
        if raw_img.mode != 'RGB':
            raw_img = raw_img.convert('RGB')
        
        img = _preprocess_image(raw_img)
 
        
        # Determine image size for model
        img_width, img_height = img.size
        imgsz = LARGE_IMAGE_SIZE if max(img_width, img_height) > LARGE_IMAGE_THRESHOLD else DEFAULT_IMAGE_SIZE
        
        model = get_model()
        if model is not None:
            results = model(img, imgsz=imgsz)
            
            if results and len(results) > 0:
                result = results[0]
                boxes_data = _extract_door_boxes(result)
                annotated = Image.fromarray(result.plot()[:, :, ::-1])
                return annotated, img, boxes_data
            
            return img, img, []
        
        if not ULTRALYTICS_AVAILABLE:
            logger.warning(f"ultralytics unavailable: {filename}")
        elif not MODEL_PATH.exists():
            logger.warning(f"Model not found: {MODEL_PATH}")
        
        return img, img, []
        
    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")
        raise ValueError(f"Failed to process {filename}: {e}") from e

