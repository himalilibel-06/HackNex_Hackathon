"""
SAFE SIGHT - CCTV Processing Pipeline with Per-Video Output Isolation

Usage:
    python pipeline.py [video_path] [optional_video_id]

Example:
    python pipeline.py videos/raw/warehouse_cctv.mp4 VID-001
"""

import sys
import os
import time
import json
import csv
import cv2
from core.video import get_video_info, list_raw_videos
from core.tracker import ByteTracker
from core.zones import ZoneManager
from core.behaviour import BehaviourAnalyzer
from core.context import ContextEngine
from core.sequence import SequenceEngine
from core.risk import RiskEngine
from core.explanation import ExplanationEngine
from core.incidents import IncidentManager
from core.evidence import EvidenceManager
from core.report import ReportGenerator


def run_pipeline(input_video_path: str,
                 video_id: str = "default",
                 model_name: str = "yolov8n.pt",
                 conf_threshold: float = 0.3,
                 progress_callback=None) -> dict:
    """
    Run Complete SafeSight AI Pipeline on a specific input video and isolate outputs per video_id.

    Parameters:
        input_video_path (str): Path to raw CCTV video.
        video_id (str): Unique video identifier (e.g. 'VID-001').
        model_name (str): YOLO model weight filename.
        conf_threshold (float): Person detection confidence threshold.

    Returns:
        dict: Real computed summary metrics dictionary.
    """
    print(f"\n[INFO] Starting SAFE SIGHT Pipeline for Video ID: {video_id}")
    print(f"[INFO] Input Video Path: {input_video_path}")

    # Define Video-Specific Output Paths
    output_video_path = f"output/annotated/{video_id}_risk.mp4"
    full_events_json = f"output/annotated/{video_id}_full_events.json"
    full_events_csv = f"output/annotated/{video_id}_full_events.csv"
    master_incidents_json = f"output/reports/{video_id}_incidents.json"
    summary_json = f"output/reports/{video_id}_summary.json"
    behaviour_csv_path = f"output/annotated/{video_id}_behaviour_data.csv"
    behaviour_json_path = f"output/annotated/{video_id}_behaviour_data.json"
    context_csv_path = f"output/annotated/{video_id}_context_events.csv"
    context_json_path = f"output/annotated/{video_id}_context_events.json"
    sequences_csv_path = f"output/annotated/{video_id}_behaviour_sequences.csv"
    sequences_json_path = f"output/annotated/{video_id}_behaviour_sequences.json"
    timelines_json_path = f"output/annotated/{video_id}_person_timelines.json"
    evidence_dir = f"output/evidence/{video_id}"
    zone_config_path = "config/zones.json"
    context_config_path = "config/context_config.json"
    risk_config_path = "config/risk_config.json"

    # 1. Validate Input Video using OpenCV
    video_info = get_video_info(input_video_path)
    if not video_info["readable"]:
        raise ValueError(f"Cannot process video: {video_info['error_message']}")

    # 2. Ensure Directories Exist
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    os.makedirs(os.path.dirname(summary_json), exist_ok=True)
    os.makedirs(evidence_dir, exist_ok=True)

    # 3. Initialize Core AI Engines
    zone_manager = ZoneManager(config_path=zone_config_path)
    behaviour_analyzer = BehaviourAnalyzer()
    context_engine = ContextEngine(config_path=context_config_path)
    sequence_engine = SequenceEngine()
    risk_engine = RiskEngine(config_path=risk_config_path)
    incident_manager = IncidentManager()
    evidence_manager = EvidenceManager(output_dir=evidence_dir)
    tracker = ByteTracker(model_name=model_name, conf_threshold=conf_threshold)

    # 4. Video Reader & Writer Setup
    cap = cv2.VideoCapture(input_video_path)
    width = video_info["width"]
    height = video_info["height"]
    fps = video_info["fps"]
    total_frames = video_info["total_frames"]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    if not out.isOpened():
        cap.release()
        raise RuntimeError(f"Failed to create VideoWriter at: {output_video_path}")

    frames_processed = 0
    full_event_records = []
    risk_scores = []
    context_evaluations_all = []
    evidence_saved_paths = []
    risk_level_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

    start_time = time.time()
    print(f"[INFO] Executing YOLOv8 + ByteTrack + Risk Analysis on {total_frames} frames...")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        frames_processed += 1
        timestamp_sec = round(frames_processed / fps, 2) if fps > 0 else 0.0

        # Run Frame Tracking + Zone + Behaviour Analysis
        active_tracks, vehicle_boxes, context_evals, annotated_frame = tracker.track_frame(
            frame, frames_processed, fps, zone_manager, behaviour_analyzer, context_engine, sequence_engine
        )

        for track_rec, c_eval in zip(active_tracks, context_evals):
            context_evaluations_all.append(c_eval)

            # Dynamic Risk Calculation
            r_eval = risk_engine.calculate_risk(track_rec, c_eval)
            score = r_eval["risk_score"]
            level = r_eval["risk_level"]
            risk_scores.append(score)
            risk_level_counts[level] = risk_level_counts.get(level, 0) + 1

            # Explanation Generation
            explanation = ExplanationEngine.generate_explanation(track_rec, c_eval, r_eval)

            # Capture Evidence Snapshot for HIGH / CRITICAL events
            ev_path = None
            if level in ["HIGH", "CRITICAL"]:
                inc_temp_id = f"INC-{video_id}-{track_rec['track_id']}"
                ev_path = evidence_manager.save_incident_snapshot(annotated_frame, inc_temp_id)
                evidence_saved_paths.append(ev_path)

            # Incident Management
            inc_obj = incident_manager.process_event(track_rec, c_eval, r_eval, explanation, ev_path)

            # Full Event Object
            full_rec = {
                "event_id": f"EVT-{video_id}-{int(timestamp_sec*100):06d}-{track_rec['track_id']}",
                "track_id": track_rec["track_id"],
                "timestamp": timestamp_sec,
                "frame": frames_processed,
                "behaviour": track_rec["behaviour"],
                "zone": track_rec["zone"],
                "context_status": c_eval["context_status"],
                "risk_score": score,
                "risk_level": level,
                "risk_reasons": r_eval["risk_reasons"],
                "explanation": explanation,
                "incident_id": inc_obj["incident_id"] if inc_obj else None,
                "evidence": [ev_path] if ev_path else []
            }
            full_event_records.append(full_rec)

            # Draw Custom Risk Badge on Frame
            x1, y1, x2, y2 = track_rec["x1"], track_rec["y1"], track_rec["x2"], track_rec["y2"]
            if level in ["HIGH", "CRITICAL"]:
                r_label = f"ID {track_rec['track_id']} | {track_rec['zone']} | {level} RISK: {score}"
                r_color = (0, 0, 255)
            elif level == "MEDIUM":
                r_label = f"ID {track_rec['track_id']} | {track_rec['zone']} | MEDIUM: {score}"
                r_color = (0, 165, 255)
            else:
                r_label = f"ID {track_rec['track_id']} | {track_rec['zone']} | NORMAL"
                r_color = (0, 255, 0)

            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), r_color, 2)
            (tw, th), _ = cv2.getTextSize(r_label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(annotated_frame, (x1, max(y1 - th - 6, 0)), (x1 + tw + 6, max(y1 - th - 6, 0) + th + 6), r_color, -1)
            cv2.putText(annotated_frame, r_label, (x1 + 3, max(y1 - th - 6, 0) + th + 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

        out.write(annotated_frame)

        if progress_callback and total_frames > 0:
            pct = min(round((frames_processed / total_frames) * 100, 1), 99.0)
            progress_callback(frames_processed, total_frames, pct)

        if frames_processed % 50 == 0 or frames_processed == total_frames:
            print(f"  -> Processed frame {frames_processed}/{total_frames} ({len(active_tracks)} active tracks)")

    # Release resources
    cap.release()
    out.release()
    elapsed_time = time.time() - start_time
    processing_fps = frames_processed / elapsed_time if elapsed_time > 0 else 0.0

    # 5. Export Video-Specific Output Data Files
    # a. Tracking & Behaviour Data
    tracker.export_tracking_csv(behaviour_csv_path)
    tracker.export_tracking_json(behaviour_json_path)

    # b. Context Events JSON & CSV
    with open(context_json_path, "w", encoding="utf-8") as f:
        json.dump(context_evaluations_all, f, indent=2)

    with open(context_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["context_event_id", "track_id", "timestamp", "cctv_time", "zone", "behaviour", "context_status", "reasons", "explanation"])
        writer.writeheader()
        for c_eval in context_evaluations_all:
            row = c_eval.copy()
            row["reasons"] = "; ".join(row["reasons"])
            writer.writerow(row)

    # c. Sequence & Timelines Export
    sequence_engine.export_data(
        timelines_json=timelines_json_path,
        sequences_json=sequences_json_path,
        sequences_csv=sequences_csv_path
    )

    # d. Full Events JSON & CSV
    with open(full_events_json, "w", encoding="utf-8") as f:
        json.dump(full_event_records, f, indent=2)

    with open(full_events_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "event_id", "track_id", "timestamp", "frame", "behaviour", "zone",
            "context_status", "risk_score", "risk_level", "risk_reasons", "explanation", "incident_id"
        ], extrasaction="ignore")
        writer.writeheader()
        for r in full_event_records:
            row = r.copy()
            row["risk_reasons"] = "; ".join(row["risk_reasons"])
            writer.writerow(row)

    # e. Incidents & Reports Export
    ReportGenerator.export_incidents_json(incident_manager.incidents, master_incidents_json)
    for inc in incident_manager.incidents:
        html_p = f"output/reports/{video_id}_incident_{inc['incident_id']}.html"
        ReportGenerator.generate_html_report(inc, output_path=html_p)

    # f. Calculate Real Unique Tracked People Count
    # Unique tracks set from ByteTrack history keys
    unique_track_ids = sorted([f"P-{tid:02d}" for tid in tracker.track_history.keys()])
    total_unique_people = len(unique_track_ids)

    # g. Calculate Real Summary Metrics
    avg_risk = round(sum(risk_scores) / len(risk_scores), 1) if risk_scores else 0.0

    summary_data = {
        "video_id": video_id,
        "input_video_name": video_info["filename"],
        "total_tracks": total_unique_people,
        "unique_track_ids": unique_track_ids,
        "total_events": len(full_event_records),
        "normal_events": risk_level_counts.get("LOW", 0),
        "unusual_events": risk_level_counts.get("MEDIUM", 0) + risk_level_counts.get("HIGH", 0) + risk_level_counts.get("CRITICAL", 0),
        "high_risk_incidents": risk_level_counts.get("HIGH", 0),
        "critical_incidents": risk_level_counts.get("CRITICAL", 0),
        "total_incidents_logged": len(incident_manager.incidents),
        "average_risk_score": avg_risk,
        "processing_time_sec": round(elapsed_time, 2),
        "output_video_path": output_video_path
    }

    ReportGenerator.export_summary(summary_data, summary_json)

    print("\n" + "=" * 65)
    print(f" SAFE SIGHT REAL AI SUMMARY FOR {video_id} ({video_info['filename']})")
    print("=" * 65)
    print(f" Input Video File          : {video_info['filename']}")
    print(f" Resolution & FPS          : {video_info['resolution']} @ {fps} FPS")
    print(f" Total Video Frames        : {total_frames}")
    print(f" COMPUTED PEOPLE TRACKED   : {total_unique_people} ({', '.join(unique_track_ids)})")
    print(f" COMPUTED TOTAL EVENTS     : {len(full_event_records)}")
    print(f" COMPUTED RISK BREAKDOWN   : LOW={risk_level_counts['LOW']}, MEDIUM={risk_level_counts['MEDIUM']}, HIGH={risk_level_counts['HIGH']}, CRITICAL={risk_level_counts['CRITICAL']}")
    print(f" COMPUTED AVG RISK SCORE   : {avg_risk}/100")
    print(f" COMPUTED INCIDENTS LOGGED : {len(incident_manager.incidents)}")
    print(f" Processing Time           : {round(elapsed_time, 2)} sec ({round(processing_fps, 2)} FPS)")
    print("=" * 65 + "\n")

    return summary_data


def main():
    video_path = sys.argv[1] if len(sys.argv) > 1 else None
    video_id = sys.argv[2] if len(sys.argv) > 2 else "VID-001"

    if not video_path:
        raw_videos = list_raw_videos("videos/raw")
        if not raw_videos:
            print("[ERROR] No video found in 'videos/raw/'.")
            sys.exit(1)
        video_path = raw_videos[0]

    run_pipeline(video_path, video_id=video_id)


if __name__ == "__main__":
    main()
