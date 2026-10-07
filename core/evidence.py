"""
SAFE SIGHT - Evidence Manager Module (core/evidence.py)

This module manages saving frame snapshots for incidents, organizing evidence files under
output/evidence/ with structured file naming (e.g. INC-001_001.jpg).
"""

import os
import cv2
import numpy as np
from typing import Optional


class EvidenceManager:
    """
    Handles capturing and saving evidence snapshots for incidents.
    """
    def __init__(self, output_dir: str = "output/evidence"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.saved_evidence_count = 0

    def save_incident_snapshot(self, frame: np.ndarray, incident_id: str) -> str:
        """
        Save a frame image snapshot associated with an incident ID.

        Parameters:
            frame (np.ndarray): BGR image frame.
            incident_id (str): Incident identifier (e.g., 'INC-001').

        Returns:
            str: Relative file path to the saved evidence image.
        """
        self.saved_evidence_count += 1
        filename = f"{incident_id}_{self.saved_evidence_count:03d}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        cv2.imwrite(filepath, frame)
        return filepath
