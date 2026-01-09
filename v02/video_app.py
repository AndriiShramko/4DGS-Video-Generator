"""
Andrii Shramko 4DGS Generator - Apple Sharp
Copyright 2025 ANDRII SHRAMKO

Desktop application for converting video frames to 3D Gaussian Splatting sequences
using Apple's SHARP model with detailed progress reporting.
"""

import sys
import os
# Enable UTF-8 output
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

import flet as ft
import threading
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import traceback
from tkinter import filedialog
import tkinter as tk
import subprocess
import platform

# Add ml-sharp to path
ml_sharp_path = Path(__file__).parent.parent / "ml-sharp" / "src"
if str(ml_sharp_path) not in sys.path:
    sys.path.insert(0, str(ml_sharp_path))

try:
    from sharp.cli.predict import DEFAULT_MODEL_URL
    from sharp.models import create_predictor, PredictorParams, RGBGaussianPredictor
    from sharp.utils import io
    from sharp.utils.gaussians import save_ply, unproject_gaussians, Gaussians3D
    import torch
    import torch.nn.functional as F
    import numpy as np
    
    @torch.no_grad()
    def predict_image_custom(
        predictor: RGBGaussianPredictor,
        image: np.ndarray,
        f_px: float,
        device: torch.device,
        internal_shape: tuple = (1536, 1536),
    ) -> Gaussians3D:
        """Predict Gaussians from an image with customizable processing resolution."""
        image_pt = torch.from_numpy(image.copy()).float().to(device).permute(2, 0, 1) / 255.0
        _, height, width = image_pt.shape
        disparity_factor = torch.tensor([f_px / width]).float().to(device)
        
        image_resized_pt = F.interpolate(
            image_pt[None],
            size=(internal_shape[1], internal_shape[0]),
            mode="bilinear",
            align_corners=True,
        )
        
        gaussians_ndc = predictor(image_resized_pt, disparity_factor)
        
        intrinsics = torch.tensor(
            [
                [f_px, 0, width / 2, 0],
                [0, f_px, height / 2, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        ).float().to(device)
        
        intrinsics_resized = intrinsics.clone()
        intrinsics_resized[0] *= internal_shape[0] / width
        intrinsics_resized[1] *= internal_shape[1] / height
        
        gaussians = unproject_gaussians(
            gaussians_ndc, torch.eye(4).to(device), intrinsics_resized, internal_shape
        )
        
        return gaussians
    
    SHARP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SHARP modules not available: {e}")
    SHARP_AVAILABLE = False

# Import PLY converter
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from convert_sharp_ply import convert_sharp_ply_to_standard
    CONVERTER_AVAILABLE = True
except ImportError:
    CONVERTER_AVAILABLE = False
    print("Warning: PLY converter not available")

# Import settings and video processor
try:
    from settings import SharpSettings
    from video_processor import VideoProcessor
    SETTINGS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Settings or video processor not available: {e}")
    SETTINGS_AVAILABLE = False

# Supported video formats
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v', '.flv', '.wmv']


class Video3DGSApp:
    """Main application class for video to PLY sequence generation."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        
        # State
        self.video_path: Optional[Path] = None
        self.video_processor: Optional[VideoProcessor] = None
        self.video_info: Optional[dict] = None
        self.output_dir: Optional[Path] = None
        self.is_processing = False
        self.model_loaded = False
        self.gaussian_predictor = None
        self.device = None
        self.last_output_dir: Optional[Path] = None
        
        # Frame range
        self.start_frame = 0
        self.end_frame = 0
        self.focal_length_px: Optional[float] = None
        
        # Settings
        if SETTINGS_AVAILABLE:
            self.settings = SharpSettings()
            self.load_paths()
        else:
            self.settings = None
            self.output_dir = Path(__file__).parent.parent / "output_video"
            self.output_dir.mkdir(exist_ok=True)
        
        # Build UI
        self.build_ui()
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = "Andrii Shramko 4DGS Generator - Apple Sharp"
        self.page.window.width = 900
        self.page.window.height = 700
        self.page.window.resizable = True
        self.page.window.min_width = 800
        self.page.window.min_height = 600
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 15
        self.page.scroll = ft.ScrollMode.AUTO
    
    def load_paths(self):
        """Load saved paths from settings."""
        if not self.settings:
            return
        
        # Load video path
        saved_video = self.settings.get("last_video_path")
        if saved_video and Path(saved_video).exists():
            self.video_path = Path(saved_video)
        
        # Load output directory
        saved_output = self.settings.get("last_output_dir")
        if saved_output:
            self.output_dir = Path(saved_output)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.output_dir = Path(__file__).parent.parent / "output_video"
            self.output_dir.mkdir(exist_ok=True)
    
    def save_paths(self):
        """Save paths to settings."""
        if not self.settings:
            return
        
        if self.video_path:
            self.settings.set("last_video_path", str(self.video_path))
        if self.output_dir:
            self.settings.set("last_output_dir", str(self.output_dir))
        
        self.settings.save()
    
    def build_ui(self):
        """Build the main UI with scrollable content and fixed generate button."""
        # Header with copyright
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.Icons.VIDEOCAM, size=32, color=ft.Colors.BLUE_400),
                            ft.Text(
                                "Andrii Shramko 4DGS Generator",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                    ft.Text(
                        "Apple Sharp",
                        size=16,
                        color=ft.Colors.GREY_400,
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        controls=[
                            ft.TextButton(
                                content=ft.Text("LinkedIn", size=12),
                                url="https://www.linkedin.com/in/andrii-shramko/",
                            ),
                            ft.Text(" | ", size=12, color=ft.Colors.GREY_500),
                            ft.TextButton(
                                content=ft.Text("Calendar", size=12),
                                url="https://calendar.app.google/K3mswrVbkAb8TTDF9",
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                "© 2025 Andrii Shramko",
                                size=11,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                    ),
                ],
                spacing=5,
            ),
            padding=15,
        )
        
        # Scrollable content area
        scrollable_content = ft.Column(
            controls=[],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        # Step 1: Video selection
        self.video_info_text = ft.Text("No video selected", size=12, color=ft.Colors.GREY_400)
        self.select_video_btn = ft.Button(
            "1. Select Video File",
            icon=ft.icons.Icons.FOLDER_OPEN,
            on_click=self.select_video,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_600,
            ),
            width=250,
        )
        
        video_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Step 1: Select Video", size=16, weight=ft.FontWeight.BOLD),
                    self.select_video_btn,
                    self.video_info_text,
                ],
                spacing=8,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=10,
        )
        
        # Step 2: Output folder selection
        self.output_dir_text = ft.Text(
            f"Output: {self.output_dir}" if self.output_dir else "No output folder selected",
            size=12,
            color=ft.Colors.GREY_400,
        )
        self.select_output_btn = ft.Button(
            "2. Select Output Folder",
            icon=ft.icons.Icons.FOLDER,
            on_click=self.select_output_folder,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600,
            ),
            width=250,
        )
        
        output_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Step 2: Select Output Folder", size=16, weight=ft.FontWeight.BOLD),
                    self.select_output_btn,
                    self.output_dir_text,
                ],
                spacing=8,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=10,
        )
        
        # Frame range selection
        self.start_frame_field = ft.TextField(
            label="Start Frame",
            value="0",
            width=120,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.end_frame_field = ft.TextField(
            label="End Frame",
            value="0",
            width=120,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.total_frames_text = ft.Text("Total: 0 frames", size=11, color=ft.Colors.GREY_400)
        
        frame_range_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Frame Range", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            self.start_frame_field,
                            ft.Text("to", size=12),
                            self.end_frame_field,
                        ],
                        spacing=10,
                    ),
                    self.total_frames_text,
                ],
                spacing=8,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=10,
        )
        
        # Focal length
        self.focal_length_field = ft.TextField(
            label="Focal Length (pixels)",
            hint_text="Auto-estimated",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        focal_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Camera Settings", size=14, weight=ft.FontWeight.BOLD),
                    self.focal_length_field,
                    ft.Text(
                        "Same for all frames (required for consistent camera)",
                        size=11,
                        color=ft.Colors.GREY_400,
                    ),
                ],
                spacing=8,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=10,
        )
        
        # Progress section
        self.progress_bar = ft.ProgressBar(value=0, color=ft.Colors.BLUE_400, width=400)
        self.progress_text = ft.Text("Ready", size=12)
        self.detailed_log = ft.Column(
            controls=[],
            spacing=3,
            scroll=ft.ScrollMode.AUTO,
            height=150,
        )
        
        progress_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Progress", size=14, weight=ft.FontWeight.BOLD),
                    self.progress_bar,
                    self.progress_text,
                    ft.Divider(height=1),
                    ft.Text("Log", size=12, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=self.detailed_log,
                        border=ft.border.all(1, ft.Colors.GREY_800),
                        border_radius=5,
                        padding=8,
                        bgcolor=ft.Colors.GREY_900,
                    ),
                ],
                spacing=8,
            ),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=10,
        )
        
        # Add all sections to scrollable content
        scrollable_content.controls.extend([
            video_section,
            output_section,
            frame_range_section,
            focal_section,
            progress_section,
        ])
        
        # Generate button - ALWAYS VISIBLE at bottom
        self.generate_btn = ft.Button(
            "3. Generate PLY Sequence",
            icon=ft.icons.Icons.PLAY_ARROW,
            on_click=self.start_generation,
            disabled=True,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600,
                padding=20,
            ),
            height=60,
            width=400,
        )
        
        # Main layout with fixed button at bottom
        main_column = ft.Column(
            controls=[
                header,
                ft.Container(
                    content=scrollable_content,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[self.generate_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(top=10, bottom=10),
                    bgcolor=ft.Colors.GREY_900,
                ),
            ],
            spacing=10,
            expand=True,
        )
        
        self.page.add(main_column)
    
    def select_video(self, e):
        """Select video file and analyze it."""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", " ".join([f"*{ext}" for ext in SUPPORTED_VIDEO_FORMATS])),
                ("All files", "*.*"),
            ],
        )
        
        root.destroy()
        
        if not file_path:
            return
        
        video_path = Path(file_path)
        
        # Check format
        if video_path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
            self.show_error(
                f"Unsupported video format: {video_path.suffix}\n\n"
                f"Supported formats: {', '.join(SUPPORTED_VIDEO_FORMATS)}"
            )
            return
        
        self.video_path = video_path
        self.add_log("INFO", f"Selected video: {self.video_path.name}")
        self.save_paths()
        
        # Analyze video
        try:
            self.video_processor = VideoProcessor(self.video_path)
            self.video_info = self.video_processor.get_info()
            
            info_str = (
                f"Frames: {self.video_info['frame_count']} | "
                f"FPS: {self.video_info['fps']:.2f} | "
                f"Resolution: {self.video_info['width']}x{self.video_info['height']} | "
                f"Duration: {self.video_info['duration_formatted']}"
            )
            self.video_info_text.value = info_str
            self.video_info_text.color = ft.Colors.WHITE
            
            self.start_frame_field.value = "0"
            self.end_frame_field.value = str(self.video_info['frame_count'] - 1)
            self.total_frames_text.value = f"Total: {self.video_info['frame_count']} frames"
            
            f_px = self.video_processor.estimate_focal_length(
                self.video_info['width'],
                self.video_info['height']
            )
            self.focal_length_px = f_px
            self.focal_length_field.value = f"{f_px:.2f}"
            
            self.add_log("SUCCESS", f"Video analyzed: {self.video_info['frame_count']} frames")
            self.add_log("INFO", f"Estimated focal length: {f_px:.2f}px")
            
            self.update_generate_button()
            self.page.update()
            
        except Exception as ex:
            self.add_log("ERROR", f"Failed to analyze video: {str(ex)}")
            self.show_error(f"Error analyzing video: {str(ex)}")
            self.page.update()
    
    def select_output_folder(self, e):
        """Select output folder for generated files."""
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        folder_path = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=str(self.output_dir) if self.output_dir else None,
        )
        
        root.destroy()
        
        if not folder_path:
            return
        
        self.output_dir = Path(folder_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_dir_text.value = f"Output: {self.output_dir}"
        self.output_dir_text.color = ft.Colors.WHITE
        
        self.add_log("INFO", f"Output folder: {self.output_dir}")
        self.save_paths()
        self.update_generate_button()
        self.page.update()
    
    def update_generate_button(self):
        """Enable/disable generate button based on state."""
        can_generate = (
            self.video_path is not None
            and self.output_dir is not None
            and not self.is_processing
        )
        self.generate_btn.disabled = not can_generate
    
    def add_log(self, level: str, message: str):
        """Add log entry to detailed log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": ft.Colors.BLUE_400,
            "SUCCESS": ft.Colors.GREEN_400,
            "WARNING": ft.Colors.YELLOW_400,
            "ERROR": ft.Colors.RED_400,
            "PROGRESS": ft.Colors.CYAN_400,
        }
        color = color_map.get(level, ft.Colors.WHITE)
        
        log_entry = ft.Text(
            f"[{timestamp}] [{level}] {message}",
            size=10,
            color=color,
        )
        self.detailed_log.controls.append(log_entry)
        
        if len(self.detailed_log.controls) > 100:
            self.detailed_log.controls.pop(0)
        
        self.page.update()
    
    def update_progress(self, value: float, message: str):
        """Update progress bar and text."""
        self.progress_bar.value = value
        self.progress_text.value = message
        self.page.update()
    
    def show_error(self, message: str):
        """Show error dialog."""
        def close_dialog(e):
            error_dialog.open = False
            self.page.update()
        
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[ft.TextButton(content=ft.Text("OK"), on_click=close_dialog)],
        )
        self.page.dialog = error_dialog
        error_dialog.open = True
        self.page.update()
    
    def show_completion_dialog(self, output_dir: Path):
        """Show completion dialog with option to open folder."""
        def close_dialog(e):
            completion_dialog.open = False
            self.page.update()
        
        def open_folder(e):
            try:
                if platform.system() == "Windows":
                    os.startfile(str(output_dir))
                elif platform.system() == "Darwin":
                    subprocess.run(["open", str(output_dir)])
                else:
                    subprocess.run(["xdg-open", str(output_dir)])
            except Exception as ex:
                self.add_log("ERROR", f"Failed to open folder: {ex}")
            close_dialog(e)
        
        completion_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Generation Complete!"),
            content=ft.Column(
                controls=[
                    ft.Text(f"PLY sequence generated successfully!"),
                    ft.Text(f"Output: {output_dir}", size=12, color=ft.Colors.GREY_400),
                ],
                spacing=10,
                tight=True,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Open Folder"),
                    on_click=open_folder,
                ),
                ft.TextButton(
                    content=ft.Text("OK"),
                    on_click=close_dialog,
                ),
            ],
        )
        self.page.dialog = completion_dialog
        completion_dialog.open = True
        self.page.update()
    
    def load_model(self):
        """Load SHARP model."""
        if self.model_loaded and self.gaussian_predictor is not None:
            return
        
        self.add_log("INFO", "Loading SHARP model...")
        self.update_progress(0.05, "Loading model...")
        
        try:
            # Determine device
            if self.settings:
                device_str = self.settings.get("device", "default")
            else:
                device_str = "default"
            
            if device_str == "default":
                if torch.cuda.is_available():
                    self.device = torch.device("cuda")
                    self.add_log("INFO", "Using CUDA device")
                elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                    self.device = torch.device("mps")
                    self.add_log("INFO", "Using MPS device")
                else:
                    self.device = torch.device("cpu")
                    self.add_log("WARNING", "Using CPU device (slower)")
            else:
                self.device = torch.device(device_str)
                self.add_log("INFO", f"Using device: {device_str}")
            
            # Determine map_location
            map_location = "cpu"
            if self.device.type == "cuda" and torch.cuda.is_available():
                map_location = "cuda"
            elif self.device.type == "mps" and hasattr(torch, "mps") and torch.mps.is_available():
                map_location = "mps"
            
            # Download checkpoint
            self.update_progress(0.1, "Downloading model checkpoint...")
            state_dict = torch.hub.load_state_dict_from_url(
                DEFAULT_MODEL_URL,
                progress=False,
                map_location=map_location
            )
            
            # Create predictor params
            params = PredictorParams()
            if self.settings:
                self.settings.apply_to_predictor_params(params)
            
            # Create predictor
            self.gaussian_predictor = create_predictor(params)
            self.gaussian_predictor.load_state_dict(state_dict)
            self.gaussian_predictor.eval()
            self.gaussian_predictor.to(self.device)
            
            self.model_loaded = True
            self.add_log("SUCCESS", "Model loaded successfully")
            self.update_progress(0.2, "Model ready")
            
        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            self.add_log("ERROR", error_msg)
            self.show_error(error_msg)
            raise
    
    def start_generation(self, e):
        """Start PLY sequence generation in background thread."""
        if self.is_processing:
            return
        
        # Validate inputs
        try:
            start_frame = int(self.start_frame_field.value)
            end_frame = int(self.end_frame_field.value)
            
            if start_frame < 0 or end_frame < start_frame:
                raise ValueError("Invalid frame range")
            
            if self.video_info and end_frame >= self.video_info['frame_count']:
                raise ValueError(f"End frame exceeds total frames ({self.video_info['frame_count']})")
            
            try:
                f_px = float(self.focal_length_field.value)
                if f_px <= 0:
                    raise ValueError("Focal length must be positive")
            except ValueError:
                raise ValueError("Invalid focal length")
            
            self.start_frame = start_frame
            self.end_frame = end_frame
            self.focal_length_px = f_px
            
        except ValueError as ve:
            self.show_error(f"Invalid input: {str(ve)}")
            return
        
        # Start processing
        self.is_processing = True
        self.generate_btn.disabled = True
        self.detailed_log.controls.clear()
        
        thread = threading.Thread(target=self.process_video, daemon=True)
        thread.start()
    
    def process_video(self):
        """Process video frames and generate PLY sequence."""
        try:
            total_frames = self.end_frame - self.start_frame + 1
            self.add_log("INFO", f"Starting generation: {total_frames} frames")
            self.add_log("INFO", f"Frame range: {self.start_frame} to {self.end_frame}")
            self.add_log("INFO", f"Focal length: {self.focal_length_px:.2f}px (same for all frames)")
            
            # Load model
            self.load_model()
            
            # Create output directory structure
            video_name = self.video_path.stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_session_dir = self.output_dir / video_name / timestamp
            output_session_dir.mkdir(parents=True, exist_ok=True)
            
            self.add_log("INFO", f"Output directory: {output_session_dir}")
            
            # Extract and process frames
            self.add_log("INFO", "Extracting frames from video...")
            frames = self.video_processor.extract_frames_range(self.start_frame, self.end_frame)
            
            if not frames:
                raise ValueError("No frames extracted from video")
            
            self.add_log("SUCCESS", f"Extracted {len(frames)} frames")
            
            # Process each frame
            for idx, (frame_num, frame_image) in enumerate(frames):
                try:
                    progress = 0.2 + (idx / len(frames)) * 0.75
                    self.update_progress(progress, f"Processing frame {frame_num} ({idx+1}/{len(frames)})...")
                    self.add_log("PROGRESS", f"Frame {frame_num}: Generating 3DGS...")
                    
                    processing_res = 1536
                    internal_shape = (processing_res, processing_res)
                    
                    # Generate 3DGS
                    gaussians = predict_image_custom(
                        self.gaussian_predictor,
                        frame_image,
                        self.focal_length_px,
                        self.device,
                        internal_shape=internal_shape,
                    )
                    
                    num_gaussians = len(gaussians.xy) if hasattr(gaussians, 'xy') else 0
                    self.add_log("SUCCESS", f"Frame {frame_num}: Generated {num_gaussians:,} Gaussians")
                    
                    # Save PLY with copyright in filename
                    height, width = frame_image.shape[:2]
                    copyright_suffix = "_Shramko_4DGS_apple-Sharp_Generator_"
                    ply_filename = f"frame_{frame_num:06d}{copyright_suffix}.ply"
                    sharp_ply = output_session_dir / ply_filename
                    
                    self.add_log("PROGRESS", f"Frame {frame_num}: Saving PLY...")
                    save_ply(gaussians, self.focal_length_px, (height, width), sharp_ply)
                    
                    # Convert to standard format
                    if CONVERTER_AVAILABLE:
                        standard_ply = output_session_dir / f"frame_{frame_num:06d}{copyright_suffix}_standard.ply"
                        convert_sharp_ply_to_standard(sharp_ply, standard_ply)
                        # Delete original
                        try:
                            sharp_ply.unlink()
                        except:
                            pass
                        self.add_log("SUCCESS", f"Frame {frame_num}: Saved {standard_ply.name}")
                    else:
                        self.add_log("SUCCESS", f"Frame {frame_num}: Saved {sharp_ply.name}")
                    
                except Exception as ex:
                    error_msg = f"Frame {frame_num}: Error - {str(ex)}"
                    self.add_log("ERROR", error_msg)
                    self.add_log("ERROR", traceback.format_exc())
                    continue
            
            # Complete
            self.last_output_dir = output_session_dir
            self.update_progress(1.0, f"Completed! Generated {len(frames)} PLY files")
            self.add_log("SUCCESS", f"Generation complete! Output: {output_session_dir}")
            
            # Show completion dialog
            self.show_completion_dialog(output_session_dir)
            
            time.sleep(1)
            self.update_progress(0, "Ready")
            
        except Exception as ex:
            error_msg = f"Fatal error: {str(ex)}\n{traceback.format_exc()}"
            self.add_log("ERROR", error_msg)
            self.update_progress(0, f"Error: {str(ex)}")
            self.show_error(error_msg)
        
        finally:
            self.is_processing = False
            self.update_generate_button()
            self.page.update()
            
            if self.video_processor:
                self.video_processor.close()


def main(page: ft.Page):
    """Main entry point."""
    app = Video3DGSApp(page)


if __name__ == "__main__":
    ft.app(target=main)

