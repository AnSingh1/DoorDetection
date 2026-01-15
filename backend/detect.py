from pdf2image import convert_from_bytes
from PIL import Image, ImageFilter
import io
import os
import numpy as np

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
        
        img = img.convert('L')
        gray = np.array(img)

        # 1. Better Thresholding
        # instead of hard 254, we use a slightly safer value OR 
        # a "percentile" based threshold if lighting varies.
        # 240 is usually safer than 254 to avoid grain, but if lines are VERY faint, 
        # you might need to stretch contrast first.
        thr = 240 
        binary_mask = (gray > thr).astype(np.uint8) # 1=Bg, 0=Line

        # 2. Optimized 3x3 Min Filter (Erosion)
        # We can use scipy for speed, or your manual shift.
        # Let's add a "Closing" step logic manually (Bridge gaps).
        # Closing = Erode (thicken black) then Dilate (shrink black).
        # But you just want THICKER, so your current Erosion is actually correct.
        # To make it stronger, we can apply it TWICE.

        def erode_manual(mask):
            pad = 1
            p = np.pad(mask, pad, mode='edge') # 'edge' padding is safer than constant 0
            neighbors = [
                p[0:-2, 0:-2], p[0:-2, 1:-1], p[0:-2, 2:],
                p[1:-1, 0:-2], p[1:-1, 1:-1], p[1:-1, 2:],
                p[2:  , 0:-2], p[2:  , 1:-1], p[2:  , 2:],
            ]
            return np.minimum.reduce(neighbors)

        # First pass: Thicken lines
        # step1 = erode_manual(binary_mask)

        # Optional Second pass: Thicken MORE (if doors are still too thin)
        # step2 = erode_manual(step1)

        img_data = binary_mask * 255 # Convert back to 0-255 grayscale
        img = Image.fromarray(img_data).convert('RGB')
 
        
        boxes_data = []
        
        # Determine imgsz based on image size - use 3200 for large images only
        img_width, img_height = img.size
        imgsz = 3200 if max(img_width, img_height) > 2000 else 640
        
        # Run YOLOv8 detection if model is available
        if model is not None:
            results = model(img, imgsz=imgsz)
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

