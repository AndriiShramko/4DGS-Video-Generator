"""
Video processing module for extracting frames from video files.
Copyright 2025 ANDRII SHRAMKO
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, List
import json


class VideoProcessor:
    """Handles video frame extraction and analysis."""
    
    def __init__(self, video_path: Path):
        """Initialize video processor with video file."""
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.cap = None
        self._info = None
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def open(self):
        """Open video file."""
        if self.cap is None:
            self.cap = cv2.VideoCapture(str(self.video_path))
            if not self.cap.isOpened():
                raise ValueError(f"Cannot open video file: {self.video_path}")
    
    def close(self):
        """Close video file."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def get_info(self) -> dict:
        """Get video information (frames, FPS, resolution, duration)."""
        if self._info is not None:
            return self._info
        
        if self.cap is None:
            self.open()
        
        # Get video properties
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        self._info = {
            "frame_count": frame_count,
            "fps": fps,
            "width": width,
            "height": height,
            "duration": duration,
            "duration_formatted": self._format_duration(duration),
        }
        
        return self._info
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to readable string."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}h {minutes}m {secs:.1f}s"
    
    def extract_frame(self, frame_number: int) -> Optional[np.ndarray]:
        """Extract specific frame by frame number (0-indexed)."""
        if self.cap is None:
            self.open()
        
        # Set frame position
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # Read frame
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame_rgb
    
    def extract_frames_range(self, start_frame: int, end_frame: int) -> List[Tuple[int, np.ndarray]]:
        """Extract frames in range [start_frame, end_frame] (inclusive)."""
        frames = []
        
        if self.cap is None:
            self.open()
        
        for frame_num in range(start_frame, end_frame + 1):
            frame = self.extract_frame(frame_num)
            if frame is not None:
                frames.append((frame_num, frame))
            else:
                break
        
        return frames
    
    def save_frame(self, frame: np.ndarray, output_path: Path):
        """Save frame as image file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_path), frame_bgr)
    
    def estimate_focal_length(self, width: int, height: int, default_fov: float = 50.0) -> float:
        """
        Estimate focal length in pixels from video dimensions.
        
        Uses common FOV assumption (50 degrees) if no EXIF data available.
        f_px = (width / 2) / tan(FOV / 2)
        """
        # Convert FOV from degrees to radians
        fov_rad = np.radians(default_fov)
        
        # Calculate focal length in pixels
        # Using width as reference (typical for landscape videos)
        f_px = (width / 2.0) / np.tan(fov_rad / 2.0)
        
        return f_px

