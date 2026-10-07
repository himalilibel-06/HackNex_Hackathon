"""
SAFE SIGHT - Behaviour Understanding Engine (core/behaviour.py)

This module receives person tracking streams and vehicle detections, computes
relative movement speed (pixels per frame), classifies basic actions (Walking,
Running, Idle/Stationary), tracks idle durations, calculates vehicle proximity,
and outputs structured behaviour records.
"""

import math
import json
import os
import numpy as np
from typing import List, Dict, Any, Tuple


class BehaviourAnalyzer:
    """
    Rule-based movement and behaviour classification engine.
    """
    def __init__(self,
                 idle_speed_threshold: float = 2.5,
                 run_speed_threshold: float = 12.0,
                 max_idle_seconds: float = 2.0,
                 vehicle_proximity_px: float = 150.0):
        """
        Initialize behaviour classification thresholds.

        Parameters:
            idle_speed_threshold (float): Movement speed below which motion is considered stationary.
            run_speed_threshold (float): Movement speed above which motion is classified as running.
            max_idle_seconds (float): Duration in seconds of stationary motion before declaring IDLE.
            vehicle_proximity_px (float): Distance threshold in pixels for vehicle proximity alerts.
        """
        self.idle_speed_threshold = idle_speed_threshold
        self.run_speed_threshold = run_speed_threshold
        self.max_idle_seconds = max_idle_seconds
        self.vehicle_proximity_px = vehicle_proximity_px

        # Per-person state: track_id -> {"low_motion_start_ts": float, "history": List[Tuple[x, y, ts]]}
        self.person_states: Dict[str, Dict[str, Any]] = {}
        # Behaviour event logs
        self.behaviour_events: List[Dict[str, Any]] = []

    def reset(self):
        """Reset state tracking."""
        self.person_states.clear()
        self.behaviour_events.clear()

    def analyze_person_behaviour(self,
                                 track_id: str,
                                 foot_point: Tuple[int, int],
                                 frame_idx: int,
                                 timestamp: float,
                                 fps: float,
                                 vehicle_boxes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze movement speed, action state, idle duration, and vehicle proximity for one person.

        Parameters:
            track_id (str): Person track identifier (e.g., 'P-01').
            foot_point (Tuple[int, int]): Current foot point coordinates (x, y).
            frame_idx (int): Current video frame number.
            timestamp (float): Current frame timestamp in seconds.
            fps (float): Video frame rate.
            vehicle_boxes (List[Dict[str, Any]]): List of detected vehicles in current frame.

        Returns:
            Dict[str, Any]: Structured behaviour classification object.
        """
        curr_x, curr_y = foot_point

        if track_id not in self.person_states:
            self.person_states[track_id] = {
                "history": [(curr_x, curr_y, timestamp)],
                "low_motion_start_ts": None,
                "current_behaviour": "Walking"
            }

        state = self.person_states[track_id]
        history = state["history"]
        history.append((curr_x, curr_y, timestamp))

        # Keep rolling window of past 10 frame positions
        if len(history) > 10:
            history.pop(0)

        # 1. Calculate Estimated Speed (pixels per frame)
        if len(history) >= 2:
            prev_x, prev_y, prev_ts = history[0]
            num_frames = len(history) - 1
            distance_px = math.hypot(curr_x - prev_x, curr_y - prev_y)
            speed_px_per_frame = round(distance_px / num_frames, 2)
        else:
            speed_px_per_frame = 0.0

        # 2. Classify Behaviour Action (Idle, Walking, Running)
        idle_duration = 0.0

        if speed_px_per_frame < self.idle_speed_threshold:
            # Low movement detected
            if state["low_motion_start_ts"] is None:
                state["low_motion_start_ts"] = timestamp

            low_motion_duration = round(timestamp - state["low_motion_start_ts"], 2)

            if low_motion_duration >= self.max_idle_seconds:
                behaviour = "Idle"
                idle_duration = low_motion_duration
            else:
                behaviour = "Walking"  # Brief pause before declaring idle
        else:
            # Motion resumed - reset low motion tracker
            state["low_motion_start_ts"] = None
            if speed_px_per_frame >= self.run_speed_threshold:
                behaviour = "Running"
            else:
                behaviour = "Walking"

        state["current_behaviour"] = behaviour

        # 3. Check Vehicle Proximity
        vehicle_nearby = False
        nearest_vehicle_dist = float("inf")
        nearest_vehicle_type = None

        for veh in vehicle_boxes:
            vx1, vy1, vx2, vy2 = veh["bbox"]
            v_center_x = (vx1 + vx2) // 2
            v_center_y = (vy1 + vy2) // 2
            dist = math.hypot(curr_x - v_center_x, curr_y - v_center_y)

            if dist < nearest_vehicle_dist:
                nearest_vehicle_dist = dist
                nearest_vehicle_type = veh.get("class_name", "Vehicle")

            if dist <= self.vehicle_proximity_px:
                vehicle_nearby = True

        result = {
            "track_id": track_id,
            "frame": frame_idx,
            "timestamp": timestamp,
            "speed_px_per_frame": speed_px_per_frame,
            "behaviour": behaviour,
            "idle_duration_sec": idle_duration,
            "vehicle_nearby": vehicle_nearby,
            "nearest_vehicle_dist": round(nearest_vehicle_dist, 1) if nearest_vehicle_dist != float("inf") else None,
            "nearest_vehicle_type": nearest_vehicle_type
        }

        # Log behaviour event if state changed or idle threshold reached
        if behaviour in ["Idle", "Running"] or vehicle_nearby:
            self.behaviour_events.append({
                "event_id": f"BE-{len(self.behaviour_events) + 1:04d}",
                "track_id": track_id,
                "behaviour": behaviour,
                "idle_duration": idle_duration,
                "vehicle_nearby": vehicle_nearby,
                "frame": frame_idx,
                "timestamp": timestamp
            })

        return result
