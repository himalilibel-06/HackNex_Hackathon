"""
SAFE SIGHT - Video Loader Module (core/video.py)

This module handles video loading, format validation, and metadata extraction
using OpenCV. It provides a simple API to inspect CCTV footage files before
passing them to downstream detection and tracking modules.
"""

import os
import cv2
from typing import Dict, Any, List, Optional

# Supported video file extensions
SUPPORTED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv'}


def is_supported_video(file_path: str) -> bool:
    """Check if the file has a supported video extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SUPPORTED_EXTENSIONS


def list_raw_videos(raw_dir: str = "videos/raw") -> List[str]:
    """Scan the raw videos directory and return all supported video file paths."""
    if not os.path.exists(raw_dir):
        return []
    
    video_files = []
    for file_name in os.listdir(raw_dir):
        full_path = os.path.join(raw_dir, file_name)
        if os.path.isfile(full_path) and is_supported_video(full_path):
            video_files.append(full_path)
    return sorted(video_files)


def get_video_info(video_path: str, verify_frames: bool = True) -> Dict[str, Any]:
    """
    Open a video file using OpenCV and extract metadata.
    
    Parameters:
        video_path (str): Path to the video file.
        verify_frames (bool): If True, tests reading the first frame to confirm validity.

    Returns:
        Dict[str, Any]: Dictionary containing video metadata and status.
    """
    result = {
        "file_path": video_path,
        "filename": os.path.basename(video_path),
        "exists": False,
        "supported": False,
        "is_opened": False,
        "width": 0,
        "height": 0,
        "resolution": "0 x 0",
        "fps": 0.0,
        "total_frames": 0,
        "duration_seconds": 0.0,
        "readable": False,
        "error_message": ""
    }

    # Step 1: Check file existence
    if not os.path.exists(video_path):
        result["error_message"] = f"File does not exist: {video_path}"
        return result
    result["exists"] = True

    # Step 2: Check file extension support
    if not is_supported_video(video_path):
        ext = os.path.splitext(video_path)[1]
        result["error_message"] = f"Unsupported video extension '{ext}'. Supported: {SUPPORTED_EXTENSIONS}"
        return result
    result["supported"] = True

    # Step 3: Attempt to open video with OpenCV
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        result["error_message"] = f"OpenCV failed to open video file: {video_path}"
        return result
    result["is_opened"] = True

    # Step 4: Extract metadata properties from OpenCV VideoCapture
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Validate FPS and compute duration
    if fps <= 0:
        result["error_message"] = f"Invalid FPS value ({fps}) returned by video stream."
        cap.release()
        return result

    duration = total_frames / fps if total_frames > 0 else 0.0

    result["width"] = width
    result["height"] = height
    result["resolution"] = f"{width} x {height}"
    result["fps"] = round(fps, 2)
    result["total_frames"] = total_frames
    result["duration_seconds"] = round(duration, 2)

    # Step 5: Verify frame readability
    if verify_frames:
        ret, frame = cap.read()
        if not ret or frame is None:
            result["error_message"] = "Video file opened, but failed to read initial frame (file may be corrupt)."
            cap.release()
            return result
        result["readable"] = True
    else:
        result["readable"] = True

    cap.release()
    return result


def print_video_info(info: Dict[str, Any]) -> None:
    """Print formatted video information to the terminal."""
    print("=" * 45)
    print(f" SAFE SIGHT - Video Metadata Inspection")
    print("=" * 45)
    print(f" Filename      : {info['filename']}")
    print(f" File Path     : {info['file_path']}")
    print(f" Exists        : {'YES' if info['exists'] else 'NO'}")
    print(f" Supported     : {'YES' if info['supported'] else 'NO'}")
    print(f" Opened        : {'YES' if info['is_opened'] else 'NO'}")
    print(f" Resolution    : {info['resolution']}")
    print(f" FPS           : {info['fps']}")
    print(f" Total Frames  : {info['total_frames']}")
    print(f" Duration      : {info['duration_seconds']} seconds")
    print(f" Readable      : {'YES' if info['readable'] else 'NO'}")
    
    if info['error_message']:
        print(f" Status/Error  : [ERROR] {info['error_message']}")
    else:
        print(f" Status        : [OK] Video validated successfully")
    print("=" * 45)
