"""
SAFE SIGHT - Video Loader Command-Line Interface

Usage:
    python video_loader.py [optional_path_to_video]

Examples:
    python video_loader.py videos/raw/sample_clip.mp4
    python video_loader.py
"""

import sys
import os
from core.video import get_video_info, print_video_info, list_raw_videos


def main():
    # If a video path is provided as a command-line argument
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # Otherwise, check for videos inside videos/raw/
        raw_videos = list_raw_videos("videos/raw")
        if not raw_videos:
            print("[INFO] No video path provided and no videos found in 'videos/raw/'.")
            print("Please place a video file (.mp4, .avi, .mov, .mkv) in 'videos/raw/' or pass a path.")
            print("Example: python video_loader.py videos/raw/clip1.mp4")
            sys.exit(1)
        video_path = raw_videos[0]
        print(f"[INFO] No video specified. Automatically selected first video found: {video_path}\n")

    # Inspect the video metadata using core OpenCV loader
    info = get_video_info(video_path)
    
    # Print formatted output
    print_video_info(info)


if __name__ == "__main__":
    main()
