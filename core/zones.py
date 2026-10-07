"""
SAFE SIGHT - Polygon Zone System Module (core/zones.py)

This module handles loading polygon zones from config/zones.json, performing
point-in-polygon tests using foot coordinates (bottom-center of bounding boxes),
and tracking zone entry/exit events and zone dwell durations for each person.
"""

import os
import json
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional


class ZoneManager:
    """
    Manages polygon zones and performs spatial queries for person foot points.
    """
    def __init__(self, config_path: str = "config/zones.json"):
        self.config_path = config_path
        self.zones: List[Dict[str, Any]] = []
        self.load_zones()

        # Track zone states per person: track_id -> {"current_zone": str, "entry_timestamp": float, "entry_frame": int}
        self.person_zone_state: Dict[str, Dict[str, Any]] = {}
        # Log of zone events: List of zone entry/exit event records
        self.zone_events: List[Dict[str, Any]] = []

    def load_zones(self):
        """Load polygon zone definitions from JSON config file."""
        if not os.path.exists(self.config_path):
            print(f"[WARNING] Zone config not found at '{self.config_path}'. Operating without zones.")
            self.zones = []
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                zones_raw = data.get("zones", [])

            self.zones = []
            for z in zones_raw:
                poly_np = np.array(z["polygon"], dtype=np.int32)
                self.zones.append({
                    "name": z["name"],
                    "type": z.get("type", "normal"),
                    "color": tuple(z.get("color", [0, 255, 0])),
                    "polygon_np": poly_np,
                    "polygon_list": z["polygon"]
                })
            print(f"[INFO] Loaded {len(self.zones)} polygon zones from '{self.config_path}'.")
        except Exception as e:
            print(f"[ERROR] Failed to parse zone config '{self.config_path}': {e}")
            self.zones = []

    def get_zone_for_point(self, point: Tuple[int, int]) -> str:
        """
        Determine which zone contains the given (x, y) foot point.

        Parameters:
            point (Tuple[int, int]): Foot coordinates (foot_x, foot_y).

        Returns:
            str: Name of containing zone or "General Area" if outside defined zones.
        """
        pt = (float(point[0]), float(point[1]))
        for z in self.zones:
            # cv2.pointPolygonTest returns >= 0 if point is inside or on edge
            result = cv2.pointPolygonTest(z["polygon_np"], pt, measureDist=False)
            if result >= 0:
                return z["name"]
        return "General Area"

    def update_person_zone(self, track_id: str, foot_point: Tuple[int, int], frame_idx: int, timestamp: float) -> Tuple[str, float]:
        """
        Update the zone state for a tracked person and record zone entry/exit events.

        Parameters:
            track_id (str): Person track identifier (e.g. 'P-01').
            foot_point (Tuple[int, int]): Foot coordinates.
            frame_idx (int): Current frame number.
            timestamp (float): Current timestamp in seconds.

        Returns:
            Tuple[str, float]: (Current zone name, Zone dwell duration in seconds).
        """
        current_zone = self.get_zone_for_point(foot_point)

        if track_id not in self.person_zone_state:
            # First time seeing person
            self.person_zone_state[track_id] = {
                "current_zone": current_zone,
                "entry_timestamp": timestamp,
                "entry_frame": frame_idx
            }
            # Record initial zone entry event
            self.zone_events.append({
                "event_id": f"ZE-{len(self.zone_events) + 1:04d}",
                "track_id": track_id,
                "event_type": "ZONE_ENTRY",
                "zone": current_zone,
                "frame": frame_idx,
                "timestamp": timestamp,
                "duration": 0.0
            })
            return current_zone, 0.0

        prev_state = self.person_zone_state[track_id]
        prev_zone = prev_state["current_zone"]
        entry_ts = prev_state["entry_timestamp"]
        dwell_duration = round(timestamp - entry_ts, 2)

        # Zone transition check
        if current_zone != prev_zone:
            # Record zone exit for old zone
            self.zone_events.append({
                "event_id": f"ZE-{len(self.zone_events) + 1:04d}",
                "track_id": track_id,
                "event_type": "ZONE_EXIT",
                "zone": prev_zone,
                "frame": frame_idx,
                "timestamp": timestamp,
                "duration": dwell_duration
            })

            # Update to new zone
            self.person_zone_state[track_id] = {
                "current_zone": current_zone,
                "entry_timestamp": timestamp,
                "entry_frame": frame_idx
            }

            # Record zone entry for new zone
            self.zone_events.append({
                "event_id": f"ZE-{len(self.zone_events) + 1:04d}",
                "track_id": track_id,
                "event_type": "ZONE_ENTRY",
                "zone": current_zone,
                "frame": frame_idx,
                "timestamp": timestamp,
                "duration": 0.0
            })
            return current_zone, 0.0

        return current_zone, dwell_duration

    def draw_zones(self, frame: np.ndarray, alpha: float = 0.25) -> np.ndarray:
        """
        Draw semi-transparent polygon zones and labels onto the image frame.

        Parameters:
            frame (np.ndarray): Original BGR frame.
            alpha (float): Transparency factor for zone overlays.

        Returns:
            np.ndarray: Annotated frame with zones drawn.
        """
        if not self.zones:
            return frame

        overlay = frame.copy()
        output = frame.copy()

        for z in self.zones:
            pts = z["polygon_np"]
            color = z["color"]
            name = z["name"]

            # Fill polygon overlay
            cv2.fillPoly(overlay, [pts], color)
            # Draw boundary line
            cv2.polylines(output, [pts], isClosed=True, color=color, thickness=2)

            # Draw Zone Label Text at top centroid of polygon
            M = cv2.moments(pts)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = pts[0][0], pts[0][1]

            (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(output, (cx - tw // 2 - 4, cy - th // 2 - 4), (cx + tw // 2 + 4, cy + th // 2 + 4), (0, 0, 0), -1)
            cv2.putText(output, name, (cx - tw // 2, cy + th // 2 - 1),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

        # Blend overlay for transparent fill effect
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        return output
