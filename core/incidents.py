"""
SAFE SIGHT - Incident Manager Engine (core/incidents.py)

This module logs HIGH and CRITICAL safety events into structured incident records,
tracking start/end timestamps, severity levels, explanations, and evidence snapshots.
"""

import os
import json
from typing import List, Dict, Any, Optional


class IncidentManager:
    """
    Manages safety incident creation and tracking.
    """
    def __init__(self):
        self.incidents: List[Dict[str, Any]] = []
        self.active_incidents: Dict[str, Dict[str, Any]] = {}

    def reset(self):
        self.incidents.clear()
        self.active_incidents.clear()

    def process_event(self, record: Dict[str, Any], context_eval: Dict[str, Any], risk_eval: Dict[str, Any], explanation: str, evidence_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Evaluate if event warrants creating or updating an open incident.

        Parameters:
            record (Dict[str, Any]): Behaviour record.
            context_eval (Dict[str, Any]): Context record.
            risk_eval (Dict[str, Any]): Risk record.
            explanation (str): Human-readable explanation.
            evidence_path (Optional[str]): Image evidence path if saved.

        Returns:
            Optional[Dict[str, Any]]: Incident object if created/updated, else None.
        """
        track_id = record["track_id"]
        timestamp = record["timestamp"]
        zone = record["zone"]
        behaviour = record["behaviour"]
        risk_score = risk_eval["risk_score"]
        risk_level = risk_eval["risk_level"]

        # Only HIGH or CRITICAL events trigger incident creation
        if risk_level not in ["HIGH", "CRITICAL"]:
            # If an active incident existed for this track, close it
            if track_id in self.active_incidents:
                self.active_incidents[track_id]["end_time"] = timestamp
                del self.active_incidents[track_id]
            return None

        # Check if an active incident is already open for this person
        if track_id in self.active_incidents:
            inc = self.active_incidents[track_id]
            inc["end_time"] = timestamp
            if risk_score > inc["risk_score"]:
                inc["risk_score"] = risk_score
                inc["risk_level"] = risk_level
            if evidence_path and evidence_path not in inc["evidence"]:
                inc["evidence"].append(evidence_path)
            return inc
        else:
            # Create new incident
            inc_id = f"INC-{len(self.incidents) + 1:03d}"
            inc = {
                "incident_id": inc_id,
                "track_id": track_id,
                "cctv_time": context_eval.get("cctv_time", "22:14"),
                "start_time": timestamp,
                "end_time": timestamp,
                "zone": zone,
                "behaviour": behaviour,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_reasons": risk_eval["risk_reasons"],
                "explanation": explanation,
                "status": "OPEN",
                "evidence": [evidence_path] if evidence_path else []
            }
            self.incidents.append(inc)
            self.active_incidents[track_id] = inc
            return inc
