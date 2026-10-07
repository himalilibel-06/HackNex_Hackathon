"""
SAFE SIGHT - Object Detector Module (core/detector.py)

This module handles object detection using Ultralytics YOLOv8.
It supports detecting both 'person' objects and relevant warehouse vehicles
(cars, trucks, buses) for proximity and safety analysis.
"""

import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from ultralytics import YOLO


class YOLODetector:
    """
    YOLOv8 Object Detector for warehouse person and vehicle detection.
    """
    # COCO Class Mapping
    COCO_CLASSES = {
        0: "Person",
        2: "Car",
        3: "Motorcycle",
        5: "Bus",
        7: "Truck"
    }

    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.3):
        """
        Initialize YOLOv8 model.

        Parameters:
            model_name (str): YOLOv8 model file name or path.
            conf_threshold (float): Confidence threshold for detections.
        """
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        
        try:
            self.model = YOLO(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model '{model_name}': {str(e)}")

    def detect_objects(self, frame: np.ndarray) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect persons and vehicles in a single frame.

        Parameters:
            frame (np.ndarray): BGR image frame from OpenCV.

        Returns:
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
                - List of person detections.
                - List of vehicle detections.
        """
        # Classes: 0=Person, 2=Car, 3=Motorcycle, 5=Bus, 7=Truck
        target_classes = list(self.COCO_CLASSES.keys())
        results = self.model(frame, conf=self.conf_threshold, classes=target_classes, verbose=False)

        person_detections = []
        vehicle_detections = []

        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                xyxy = box.xyxy[0].cpu().numpy().astype(int).tolist()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = self.COCO_CLASSES.get(cls_id, "Object")

                x1, y1, x2, y2 = xyxy
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                foot_x = center_x
                foot_y = y2

                det_obj = {
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(conf, 2),
                    "class_name": cls_name,
                    "class_id": cls_id,
                    "center": (center_x, center_y),
                    "foot_point": (foot_x, foot_y)
                }

                if cls_id == 0:
                    person_detections.append(det_obj)
                else:
                    vehicle_detections.append(det_obj)

        return person_detections, vehicle_detections

    def detect_persons(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Legacy helper returning person detections only."""
        persons, _ = self.detect_objects(frame)
        return persons

    def draw_detections(self, frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
        """Draw bounding boxes and labels for person & vehicle detections on frame."""
        annotated_frame = frame.copy()

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            cls_name = det["class_name"]
            label = f"{cls_name} {conf:.2f}"

            color = (0, 255, 0) if cls_name == "Person" else (0, 165, 255)

            # Draw Box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

            # Draw Label
            (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            label_y1 = max(y1 - text_h - 6, 0)
            cv2.rectangle(annotated_frame, (x1, label_y1), (x1 + text_w + 6, label_y1 + text_h + 6), color, -1)
            cv2.putText(annotated_frame, label, (x1 + 3, label_y1 + text_h + 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            # Draw Foot Point marker for Persons
            if cls_name == "Person":
                foot_x, foot_y = det["foot_point"]
                cv2.circle(annotated_frame, (foot_x, foot_y), 4, (0, 0, 255), -1)

        return annotated_frame
