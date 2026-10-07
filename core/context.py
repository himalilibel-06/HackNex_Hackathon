"""
SAFE SIGHT - Context Engine Module (core/context.py)

This module evaluates person behaviour within environmental context:
Location + Shift Time + Dwell Duration + Vehicle Proximity.
It classifies events into 'normal', 'potentially_unusual', or 'potential_safety_concern'
and generates human-readable explanations answering WHO, WHAT, WHERE, WHEN, and WHY.
"""

import os
import json
from typing import Dict, Any, List, Optional


class ContextEngine:
    """
    Rule-based context-aware safety evaluation engine.
    """
    def __init__(self, config_path: str = "config/context_config.json"):
        self.config_path = config_path
        self.config = {
            "working_hours": {"start": "08:00", "end": "18:00"},
            "simulated_cctv_time": "22:14",
            "is_outside_shift": True,
            "restricted_zones": ["Restricted Area"],
            "vehicle_sensitive_zones": ["Vehicle Lane"],
            "max_allowed_idle_seconds_in_restricted": 5.0
        }
        self.load_config()

    def load_config(self):
        """Load context configuration rules from JSON file."""
        if not os.path.exists(self.config_path):
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.config.update(data)
        except Exception as e:
            print(f"[ERROR] Failed to load context config '{self.config_path}': {e}")

    def evaluate_context(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate context for a single person tracking & behaviour record.

        Parameters:
            record (Dict[str, Any]): Behaviour record containing track_id, zone, behaviour,
                                     zone_duration_sec, idle_duration_sec, vehicle_nearby, timestamp.

        Returns:
            Dict[str, Any]: Structured API-ready context evaluation object.
        """
        track_id = record["track_id"]
        zone = record["zone"]
        behaviour = record["behaviour"]
        idle_duration = record.get("idle_duration_sec", 0.0)
        zone_duration = record.get("zone_duration_sec", 0.0)
        vehicle_nearby = record.get("vehicle_nearby", False)
        timestamp = record["timestamp"]
        cctv_time = self.config.get("simulated_cctv_time", "22:14")

        restricted_zones = self.config.get("restricted_zones", ["Restricted Area"])
        is_outside_shift = self.config.get("is_outside_shift", True)
        max_idle_restricted = self.config.get("max_allowed_idle_seconds_in_restricted", 5.0)

        status = "normal"
        reasons = []

        # 1. Restricted Zone + Shift Hours Context Check
        if zone in restricted_zones:
            if is_outside_shift:
                status = "potentially_unusual"
                reasons.append("Restricted zone entry outside working shift hours")

            if behaviour == "Idle" and idle_duration >= max_idle_restricted:
                status = "potentially_unusual"
                reasons.append(f"Extended stationary dwell ({idle_duration:.0f}s) in restricted area")

        # 2. Vehicle Proximity Safety Check
        if vehicle_nearby:
            status = "potential_safety_concern" if status == "normal" else status
            reasons.append("Worker in close proximity to moving vehicle/lane")

        # 3. Construct Explanation (WHO, WHAT, WHERE, WHEN, WHY)
        if status == "normal":
            explanation = f"Person {track_id} was {behaviour.lower()} in {zone} during expected operations."
        elif status == "potentially_unusual":
            reason_str = " and ".join(reasons)
            explanation = (f"Person {track_id} entered {zone} at {cctv_time} (timestamp {timestamp:.1f}s), "
                           f"performing '{behaviour}' for {zone_duration:.1f}s. Why unusual: {reason_str}.")
        else:
            reason_str = " and ".join(reasons)
            explanation = (f"Person {track_id} at {cctv_time} in {zone} triggered a safety alert. "
                           f"Reason: {reason_str}.")

        return {
            "context_event_id": f"CTX-{int(timestamp*100):06d}",
            "track_id": track_id,
            "timestamp": timestamp,
            "cctv_time": cctv_time,
            "zone": zone,
            "behaviour": behaviour,
            "context_status": status,
            "reasons": reasons if reasons else ["Normal work activity"],
            "explanation": explanation
        }
