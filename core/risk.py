"""
SAFE SIGHT - Risk Scoring Engine (core/risk.py)

This module calculates interpretable risk scores (0–100) based on configurable
policy weights (restricted zone entry, shift hours, idle dwell, vehicle proximity).
Risk levels are categorized into LOW, MEDIUM, HIGH, and CRITICAL with itemized reasons.
"""

import os
import json
from typing import Dict, Any, List, Tuple


class RiskEngine:
    """
    Configurable policy-based risk calculation engine.
    """
    def __init__(self, config_path: str = "config/risk_config.json"):
        self.config_path = config_path
        self.config = {
            "weights": {
                "restricted_zone": 30,
                "after_hours": 20,
                "idle_in_restricted_zone": 20,
                "vehicle_nearby": 25,
                "running": 10,
                "long_stationary_duration": 10
            },
            "levels": {
                "low_max": 29,
                "medium_max": 59,
                "high_max": 79
            }
        }
        self.load_config()

    def load_config(self):
        """Load risk weights and thresholds from JSON configuration."""
        if not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.config.update(data)
        except Exception as e:
            print(f"[ERROR] Failed to load risk config '{self.config_path}': {e}")

    def calculate_risk(self, record: Dict[str, Any], context_eval: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk score, level, and itemized contributing factors for a single event.

        Parameters:
            record (Dict[str, Any]): Behaviour record.
            context_eval (Dict[str, Any]): Context evaluation record.

        Returns:
            Dict[str, Any]: Risk evaluation object containing score, level, and reasons.
        """
        weights = self.config.get("weights", {})
        levels = self.config.get("levels", {"low_max": 29, "medium_max": 59, "high_max": 79})

        zone = record.get("zone", "General Area")
        behaviour = record.get("behaviour", "Walking")
        idle_duration = record.get("idle_duration_sec", 0.0)
        vehicle_nearby = record.get("vehicle_nearby", False)

        c_status = context_eval.get("context_status", "normal")
        c_reasons = context_eval.get("reasons", [])

        score = 0
        reasons = []
        factors = {}

        # 1. Restricted Zone Entry (+30)
        if zone == "Restricted Area":
            add_val = weights.get("restricted_zone", 30)
            score += add_val
            reasons.append("Restricted zone entry")
            factors["restricted_zone"] = f"+{add_val}"

        # 2. Outside Shift Hours (+20)
        if any("outside working" in r.lower() or "shift" in r.lower() for r in c_reasons) or c_status != "normal":
            if zone == "Restricted Area":
                add_val = weights.get("after_hours", 20)
                score += add_val
                reasons.append("Activity outside configured working hours")
                factors["after_hours"] = f"+{add_val}"

        # 3. Idle in Restricted Zone (+20)
        if zone == "Restricted Area" and behaviour == "Idle":
            add_val = weights.get("idle_in_restricted_zone", 20)
            score += add_val
            reasons.append("Stationary dwell inside restricted zone")
            factors["idle_in_restricted_zone"] = f"+{add_val}"

        # 4. Vehicle Proximity (+25)
        if vehicle_nearby:
            add_val = weights.get("vehicle_nearby", 25)
            score += add_val
            reasons.append("Worker in close proximity to vehicle")
            factors["vehicle_nearby"] = f"+{add_val}"

        # 5. Running (+10)
        if behaviour == "Running":
            add_val = weights.get("running", 10)
            score += add_val
            reasons.append("Running motion detected")
            factors["running"] = f"+{add_val}"

        # 6. Long Stationary Duration (>10s) (+10)
        if idle_duration >= 10.0:
            add_val = weights.get("long_stationary_duration", 10)
            score += add_val
            reasons.append(f"Extended idle duration ({idle_duration:.0f}s)")
            factors["long_stationary_duration"] = f"+{add_val}"

        # Clamp score to [0, 100]
        final_score = min(max(score, 0), 100)

        # Map to Risk Level
        if final_score <= levels.get("low_max", 29):
            risk_level = "LOW"
        elif final_score <= levels.get("medium_max", 59):
            risk_level = "MEDIUM"
        elif final_score <= levels.get("high_max", 79):
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        if not reasons:
            reasons.append("Normal warehouse movement")

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "risk_reasons": reasons,
            "contributing_factors": factors
        }
