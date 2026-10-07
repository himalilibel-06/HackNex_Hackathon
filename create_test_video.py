"""
Script to create a synthetic sample video for testing Phase 2 video loader.
Generates a 5-second 1280x720 30fps video in videos/raw/sample_warehouse.mp4.
"""

import os
import cv2
import numpy as np

def generate_sample_video(output_path="videos/raw/sample_warehouse.mp4", duration_sec=5, fps=30, width=1280, height=720):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = duration_sec * fps
    for i in range(total_frames):
        # Create a dark grey background frame (simulating CCTV background)
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (40, 40, 40)
        
        # Add frame index text
        cv2.putText(frame, f"SAFE SIGHT CCTV TEST FRAME #{i+1}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        cv2.putText(frame, f"Resolution: {width}x{height} | FPS: {fps}", (50, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)

        out.write(frame)

    out.release()
    print(f"Sample video created successfully at: {output_path}")

if __name__ == "__main__":
    generate_sample_video()
