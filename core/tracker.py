"""
SAFE SIGHT - ByteTrack Person Tracker with Context & Sequence Integration (core/tracker.py)

This module handles multi-object person tracking, connects zone checking,
behaviour classification, context interpretation, and sequence tracking.
"""

import os
import cv2
import json
import csv
import numpy as np
from typing import List, Dict, Any, Tuple
from ultralytics import YOLO
from core.zones import ZoneManager
from core.behaviour import BehaviourAnalyzer
from core.context import ContextEngine
from core.sequence import SequenceEngine


class ByteTracker:
    """
    ByteTrack-backed person tracker integrated with Zone, Behaviour, Context, and Sequence engines.
    """
    COCO_VEHICLE_CLASSES = [2, 3, 5, 7]  # Car, Motorcycle, Bus, Truck

    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.3, tracker_type: str = "bytetrack.yaml"):
        self.model_name = model_name
        self.conf_threshold = conf_threshold
        self.tracker_type = tracker_type
        
        try:
            self.model = YOLO(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model '{model_name}': {str(e)}")

        self.track_history: Dict[int, List[Dict[str, Any]]] = {}

    def reset(self):
        """Reset tracker history."""
        self.track_history.clear()

    def track_frame(self,
                    frame: np.ndarray,
                    frame_idx: int,
                    fps: float,
                    zone_manager: ZoneManager,
                    behaviour_analyzer: BehaviourAnalyzer,
                    context_engine: ContextEngine = None,
                    sequence_engine: SequenceEngine = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], np.ndarray]:
        """
        Track persons, detect vehicles, update zones, evaluate context, and build timelines for one frame.

        Parameters:
            frame (np.ndarray): Input image frame.
            frame_idx (int): Current frame number.
            fps (float): Video FPS.
            zone_manager (ZoneManager): Polygon zone engine.
            behaviour_analyzer (BehaviourAnalyzer): Movement behaviour engine.
            context_engine (ContextEngine): Context-aware intelligence engine.
            sequence_engine (SequenceEngine): Behaviour sequence engine.

        Returns:
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], np.ndarray]:
                - Active tracked person records.
                - Detected vehicle records.
                - Context evaluation results list.
                - Fully annotated BGR output frame.
        """
        timestamp_sec = round(frame_idx / fps, 2) if fps > 0 else 0.0

        # 1. Detect Vehicles (Classes 2, 3, 5, 7)
        vehicle_results = self.model(frame, conf=self.conf_threshold, classes=self.COCO_VEHICLE_CLASSES, verbose=False)
        vehicle_boxes = []

        if len(vehicle_results) > 0 and vehicle_results[0].boxes is not None:
            v_boxes = vehicle_results[0].boxes
            for v_box in v_boxes:
                v_xyxy = v_box.xyxy[0].cpu().numpy().astype(int).tolist()
                v_conf = float(v_box.conf[0].cpu().numpy())
                v_cls_id = int(v_box.cls[0].cpu().numpy())
                v_cls_name = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}.get(v_cls_id, "Vehicle")
                vehicle_boxes.append({
                    "bbox": v_xyxy,
                    "confidence": round(v_conf, 2),
                    "class_name": v_cls_name
                })

        # 2. Draw Zone Overlays
        annotated_frame = zone_manager.draw_zones(frame, alpha=0.25)

        # 3. Draw Vehicles
        for veh in vehicle_boxes:
            vx1, vy1, vx2, vy2 = veh["bbox"]
            v_label = f"{veh['class_name']} {veh['confidence']:.2f}"
            cv2.rectangle(annotated_frame, (vx1, vy1), (vx2, vy2), (0, 165, 255), 2)
            cv2.putText(annotated_frame, v_label, (vx1, vy1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)

        # 4. Run ByteTrack on Person Class [0]
        track_results = self.model.track(
            source=frame,
            persist=True,
            tracker=self.tracker_type,
            conf=self.conf_threshold,
            classes=[0],
            verbose=False
        )

        current_frame_tracks = []
        context_evaluations = []

        if len(track_results) > 0 and track_results[0].boxes is not None:
            boxes = track_results[0].boxes

            if boxes.id is not None:
                track_ids = boxes.id.cpu().numpy().astype(int).tolist()
                xyxys = boxes.xyxy.cpu().numpy().astype(int).tolist()
                confs = boxes.conf.cpu().numpy().tolist()

                for track_id, xyxy, conf in zip(track_ids, xyxys, confs):
                    x1, y1, x2, y2 = xyxy
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    foot_x = center_x
                    foot_y = y2
                    pid_str = f"P-{track_id:02d}"
                    foot_pt = (foot_x, foot_y)

                    # Spatial Zone Analysis
                    current_zone, zone_duration = zone_manager.update_person_zone(pid_str, foot_pt, frame_idx, timestamp_sec)

                    # Behaviour Analysis
                    b_info = behaviour_analyzer.analyze_person_behaviour(
                        pid_str, foot_pt, frame_idx, timestamp_sec, fps, vehicle_boxes
                    )

                    behaviour = b_info["behaviour"]
                    speed = b_info["speed_px_per_frame"]
                    idle_duration = b_info["idle_duration_sec"]
                    vehicle_nearby = b_info["vehicle_nearby"]

                    track_record = {
                        "track_id": pid_str,
                        "raw_id": track_id,
                        "frame": frame_idx,
                        "timestamp": timestamp_sec,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                        "center_x": center_x,
                        "center_y": center_y,
                        "foot_x": foot_x,
                        "foot_y": foot_y,
                        "speed_px_per_frame": speed,
                        "behaviour": behaviour,
                        "zone": current_zone,
                        "zone_duration_sec": zone_duration,
                        "idle_duration_sec": idle_duration,
                        "vehicle_nearby": vehicle_nearby,
                        "confidence": round(conf, 2)
                    }

                    # Context Evaluation
                    if context_engine:
                        c_eval = context_engine.evaluate_context(track_record)
                        context_evaluations.append(c_eval)
                        track_record["context_status"] = c_eval["context_status"]
                        track_record["explanation"] = c_eval["explanation"]

                        # Sequence & Timeline Update
                        if sequence_engine:
                            sequence_engine.update_timeline(track_record, c_eval)

                    current_frame_tracks.append(track_record)

                    if track_id not in self.track_history:
                        self.track_history[track_id] = []
                    self.track_history[track_id].append(track_record)

                    # --- Draw Context-Aware Annotations ---
                    c_status = track_record.get("context_status", "normal")
                    if c_status == "potentially_unusual":
                        label = f"ID {pid_str} | {behaviour} | {current_zone} | UNUSUAL"
                        box_color = (0, 0, 255)  # Bright Red for Unusual
                    elif c_status == "potential_safety_concern":
                        label = f"ID {pid_str} | {behaviour} | {current_zone} | CAUTION"
                        box_color = (0, 165, 255)  # Orange/Yellow for Caution
                    else:
                        label = f"ID {pid_str} | {behaviour} | {current_zone} | Normal"
                        box_color = (0, 255, 0)  # Green for Normal

                    # Draw Box
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), box_color, 2)

                    # Label Box Header
                    (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                    label_y1 = max(y1 - th - 6, 0)
                    cv2.rectangle(annotated_frame, (x1, label_y1), (x1 + tw + 6, label_y1 + th + 6), box_color, -1)

                    # Label Text
                    cv2.putText(annotated_frame, label, (x1 + 3, label_y1 + th + 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

                    # Draw Foot Point marker
                    cv2.circle(annotated_frame, (foot_x, foot_y), 4, (0, 0, 255), -1)

                    # Motion Trail
                    hist_pts = [(r["center_x"], r["center_y"]) for r in self.track_history[track_id][-15:]]
                    for i in range(1, len(hist_pts)):
                        cv2.line(annotated_frame, hist_pts[i-1], hist_pts[i], (0, 255, 255), 2)

        return current_frame_tracks, vehicle_boxes, context_evaluations, annotated_frame

    def export_tracking_csv(self, output_csv_path: str):
        """Export comprehensive tracking, behaviour, & context data to CSV."""
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        fieldnames = [
            "track_id", "raw_id", "frame", "timestamp", "x1", "y1", "x2", "y2",
            "center_x", "center_y", "foot_x", "foot_y", "speed_px_per_frame",
            "behaviour", "zone", "zone_duration_sec", "idle_duration_sec", "vehicle_nearby",
            "context_status", "confidence"
        ]

        with open(output_csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for track_id in sorted(self.track_history.keys()):
                for record in self.track_history[track_id]:
                    writer.writerow(record)

    def export_tracking_json(self, output_json_path: str):
        """Export comprehensive tracking, behaviour, & context data to JSON."""
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        export_data = {}
        for track_id, records in self.track_history.items():
            export_data[f"P-{track_id:02d}"] = records

        with open(output_json_path, mode="w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)
