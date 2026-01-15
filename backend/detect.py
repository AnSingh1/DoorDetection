import pdf2image
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    YOLO = None

# Load the YOLOv8 model if available
MODEL_PATH = "backend/best.pt"
model = None
if ULTRALYTICS_AVAILABLE and os.path.exists(MODEL_PATH):
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"Warning: Could not load model {MODEL_PATH}: {e}")



from typing import Tuple, List, Dict

def detect(file_content: bytes, filename: str) -> Tuple[Image.Image, Image.Image, List[Dict]]:
    """
    Process a PDF or image file and run YOLOv8 detection if available.
    
    Args:
        file_content: The file bytes
        filename: The filename to determine file type
    
    Returns:
        Tuple of (annotated_image, original_image, boxes_data)
        - annotated_image: PIL Image with bounding boxes and annotations
        - original_image: PIL Image without annotations
        - boxes_data: List of dictionaries with box coordinates and class info
        
    Raises:
        Exception: If file processing fails
    """
    try:
        # Determine file type and convert to image
        if filename.lower().endswith('.pdf'):
            # Convert PDF to images (300 dpi)
            images = convert_from_bytes(file_content, dpi=300)
            # Use the first page if multiple pages
            img = images[0]
        else:
            # Load image directly from bytes
            img = Image.open(io.BytesIO(file_content))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        boxes_data = []
        
        # Run YOLOv8 detection if model is available
        if model is not None:
            results = model(img)
            # Get the annotated image from results
            if results and len(results) > 0:
                result = results[0]
                
                # Filter to keep only doors by class name
                if result.boxes is not None and len(result.boxes) > 0:
                    # Get class names from the model
                    class_names = result.names  # Dictionary of class_id: class_name
                    
                    # Find the class ID for 'door'
                    door_class_id = None
                    for class_id, class_name in class_names.items():
                        if class_name.lower() == 'door':
                            door_class_id = class_id
                            break
                    
                    # If we found the door class, filter for it
                    if door_class_id is not None:
                        # Create a mask for door class
                        door_mask = result.boxes.cls == door_class_id
                        
                        if door_mask.any():
                            # Create a copy of boxes with only doors
                            filtered_boxes = result.boxes[door_mask]
                            result.boxes = filtered_boxes
                            
                            # Extract box data for frontend
                            import numpy as np
                            for box in filtered_boxes:
                                xyxy = box.xyxy[0].cpu().numpy()  # Get coordinates
                                x1, y1, x2, y2 = xyxy.astype(int)
                                boxes_data.append({
                                    "x": int(x1),
                                    "y": int(y1),
                                    "width": int(x2 - x1),
                                    "height": int(y2 - y1),
                                    "className": "Door",
                                    "confidence": float(box.conf[0].cpu().numpy())
                                })
                    else:
                        print(f"Warning: 'door' class not found in model. Available classes: {list(class_names.values())}")
                
                # Plot the filtered results
                result_img = Image.fromarray(result.plot()[:, :, ::-1])
                return result_img, img, boxes_data
            else:
                # If no results, return original image
                return img, img, []
        else:
            # If model is not available, return the image as is
            if not ULTRALYTICS_AVAILABLE:
                print(f"Warning: ultralytics not available. Returning original image for {filename}")
            elif not os.path.exists(MODEL_PATH):
                print(f"Warning: Model file {MODEL_PATH} not found. Returning original image for {filename}")
            return img, img, []
            
    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
        raise Exception(f"Error processing {filename}: {str(e)}")

