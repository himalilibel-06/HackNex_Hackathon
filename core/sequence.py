"""
SAFE SIGHT - Behaviour Sequence Engine Module (core/sequence.py)

This module builds per-person ordered activity sequences over time, constructs
chronological person timelines, evaluates multi-event behavioural patterns
(e.g., Entrance -> Walk -> Restricted Entry -> Extended Stay), and generates
structured API-ready sequence data.
"""

import os
import json
import csv
from typing import List, Dict, Any, Tuple, Optional


class SequenceEngine:
    """
    Builds per-person activity timelines and evaluates multi-event behaviour sequences.
    """
    def __init__(self):
        # Per-person chronological events: track_id -> List of event dicts
        self.person_timelines: Dict[str, List[Dict[str, Any]]] = {}
        # Track last recorded state per person to avoid duplicate events
        self.last_state: Dict[str, Dict[str, Any]] = {}
        # Detected high-level behaviour sequences
        self.sequences: List[Dict[str, Any]] = []

    def reset(self):
        """Reset sequence trackers."""
        self.person_timelines.clear()
        self.last_state.clear()
        self.sequences.clear()

    def update_timeline(self, record: Dict[str, Any], context_eval: Dict[str, Any]):
        """
        Add a frame record to the person's chronological activity timeline.

        Parameters:
            record (Dict[str, Any]): Behaviour record.
            context_eval (Dict[str, Any]): Context evaluation object.
        """
        track_id = record["track_id"]
        timestamp = record["timestamp"]
        zone = record["zone"]
        behaviour = record["behaviour"]
        status = context_eval["context_status"]

        if track_id not in self.person_timelines:
            self.person_timelines[track_id] = []
            self.last_state[track_id] = {"zone": None, "behaviour": None}

        last = self.last_state[track_id]

        # Only record discrete timeline events when zone or behaviour changes
        if zone != last["zone"] or behaviour != last["behaviour"]:
            event_type = "ZONE_ENTRY" if zone != last["zone"] else "ACTION_CHANGE"
            timeline_event = {
                "timestamp": timestamp,
                "cctv_time": context_eval.get("cctv_time", "22:14"),
                "event_type": event_type,
                "behaviour": behaviour,
                "zone": zone,
                "status": status,
                "description": f"{behaviour.capitalize()} in {zone}"
            }
            self.person_timelines[track_id].append(timeline_event)
            self.last_state[track_id] = {"zone": zone, "behaviour": behaviour}

            # Evaluate sequence patterns whenever a new discrete event is added
            self._evaluate_patterns(track_id)

    def _evaluate_patterns(self, track_id: str):
        """Evaluate if the person's timeline matches a known suspicious sequence pattern."""
        timeline = self.person_timelines[track_id]
        if len(timeline) < 2:
            return

        zones_visited = [e["zone"] for e in timeline]
        behaviours = [e["behaviour"] for e in timeline]
        statuses = [e["status"] for e in timeline]

        # Pattern 1: Entrance/Walk -> Restricted Area -> Idle
        if "Restricted Area" in zones_visited and "Idle" in behaviours:
            seq_id = f"SEQ-{track_id}-{len(self.sequences)+1:03d}"
            # Check if sequence already recorded for this track
            if not any(s["track_id"] == track_id and s["pattern_type"] == "RESTRICTED_IDLE" for s in self.sequences):
                self.sequences.append({
                    "sequence_id": seq_id,
                    "track_id": track_id,
                    "pattern_type": "RESTRICTED_IDLE",
                    "start_time": timeline[0]["timestamp"],
                    "end_time": timeline[-1]["timestamp"],
                    "events": [e["description"] for e in timeline],
                    "zones": list(dict.fromkeys(zones_visited)),
                    "context_status": "potentially_unusual",
                    "explanation": f"Person {track_id} entered Restricted Area and remained stationary."
                })

        # Pattern 2: Normal Walk -> Vehicle Zone -> Safety Alert
        if "Vehicle Lane" in zones_visited:
            seq_id = f"SEQ-{track_id}-{len(self.sequences)+1:03d}"
            if not any(s["track_id"] == track_id and s["pattern_type"] == "VEHICLE_APPROACH" for s in self.sequences):
                self.sequences.append({
                    "sequence_id": seq_id,
                    "track_id": track_id,
                    "pattern_type": "VEHICLE_APPROACH",
                    "start_time": timeline[0]["timestamp"],
                    "end_time": timeline[-1]["timestamp"],
                    "events": [e["description"] for e in timeline],
                    "zones": list(dict.fromkeys(zones_visited)),
                    "context_status": "potential_safety_concern",
                    "explanation": f"Person {track_id} moved into Vehicle Lane near active traffic."
                })

    def export_data(self,
                    timelines_json: str = "output/annotated/person_timelines.json",
                    sequences_json: str = "output/annotated/behaviour_sequences.json",
                    sequences_csv: str = "output/annotated/behaviour_sequences.csv"):
        """Export API-ready structured JSON and CSV files."""
        os.makedirs(os.path.dirname(timelines_json), exist_ok=True)

        # 1. Export Person Timelines JSON
        with open(timelines_json, "w", encoding="utf-8") as f:
            json.dump(self.person_timelines, f, indent=2)

        # 2. Export Sequences JSON
        with open(sequences_json, "w", encoding="utf-8") as f:
            json.dump(self.sequences, f, indent=2)

        # 3. Export Sequences CSV
        fieldnames = ["sequence_id", "track_id", "pattern_type", "start_time", "end_time", "zones", "context_status", "explanation"]
        with open(sequences_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for seq in self.sequences:
                row = seq.copy()
                row["zones"] = " -> ".join(row["zones"])
                row.pop("events", None)
                writer.writerow(row)
