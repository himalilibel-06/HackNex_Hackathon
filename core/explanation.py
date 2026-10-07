"""
SAFE SIGHT - Explainable Alert Engine (core/explanation.py)

This module formats transparent, human-readable alerts answering WHO, WHAT,
WHERE, WHEN, WHY, and RISK level for safety incidents and routine events.
"""

from typing import Dict, Any, List


class ExplanationEngine:
    """
    Generates explainable human-readable alert strings.
    """
    @staticmethod
    def generate_explanation(record: Dict[str, Any], context_eval: Dict[str, Any], risk_eval: Dict[str, Any]) -> str:
        """
        Generate structured explanation text.
        """
        track_id = record["track_id"]
        zone = record["zone"]
        behaviour = record["behaviour"]
        timestamp = record["timestamp"]
        cctv_time = context_eval.get("cctv_time", "22:14")
        
        score = risk_eval["risk_score"]
        level = risk_eval["risk_level"]
        reasons = risk_eval["risk_reasons"]

        reason_str = "; ".join(reasons)

        if level in ["HIGH", "CRITICAL"]:
            return (f"ALERT [{level} RISK - {score}/100]: Person {track_id} entered {zone} at {cctv_time} "
                    f"(timestamp {timestamp:.1f}s) performing '{behaviour}'. Reasons: {reason_str}.")
        elif level == "MEDIUM":
            return (f"NOTICE [{level} RISK - {score}/100]: Person {track_id} in {zone} at {cctv_time} "
                    f"performing '{behaviour}'. Reasons: {reason_str}.")
        else:
            return (f"NORMAL [LOW RISK - {score}/100]: Person {track_id} walking in {zone} during expected shift. "
                    f"No safety violations detected.")
