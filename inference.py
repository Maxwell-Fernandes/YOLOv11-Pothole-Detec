import cv2
import supervision as sv
from ultralytics import YOLO
import numpy as np
import base64

# Load YOLO model
model_loaded = YOLO('best.pt')

# Define class names (should match your trained dataset)
CLASS_NAMES = ['0']  # Add more if your model has multiple classes

# Annotators
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

def predict(image_file):
    # Read image from request.files['image']
    file_bytes = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not decode image")

    # Run YOLO inference
    results = model_loaded(image, conf=0.33)[0]

    # Parse detections
    detections = sv.Detections.from_ultralytics(results)

    # Create readable labels
    labels = [
        f"{CLASS_NAMES[class_id]} {confidence:.2f}"
        for class_id, confidence in zip(detections.class_id, detections.confidence)
    ]

    # Annotate image
    annotated_image = box_annotator.annotate(scene=image.copy(), detections=detections)
    annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections, labels=labels)

    # Encode image to base64
    success, buffer = cv2.imencode('.jpg', annotated_image)
    if not success:
        raise ValueError("Failed to encode image")
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    # Build detection data
    detection_data = []
    for class_id, confidence, box in zip(detections.class_id, detections.confidence, detections.xyxy):
        detection_data.append({
            "label": CLASS_NAMES[class_id],
            "confidence": float(confidence),
            "bbox": [int(coord) for coord in box]
        })

    return {
        "detections": detection_data,
        "annotated_image": encoded_image
    }
