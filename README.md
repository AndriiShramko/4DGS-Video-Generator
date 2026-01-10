# Andrii Shramko 4DGS Generator - Apple Sharp

**Professional Desktop Application for Converting Video Frames to 4D Gaussian Splatting Sequences**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5.1%2Bcu121-orange.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Windows](https://img.shields.io/badge/Windows-10%2B-blue.svg)](https://www.microsoft.com/windows)

## 🎯 Overview

This is a complete, production-ready desktop application for generating high-quality 4D Gaussian Splatting (4DGS) sequences from video files using Apple's state-of-the-art [SHARP model](https://github.com/apple/ml-sharp). The application features a modern GUI, comprehensive quality settings, batch frame processing, and automatic optimization for your hardware configuration.

### Key Features

- 🎬 **Video to 4DGS Sequence**: Convert video frames to 4D Gaussian Splatting models
- 🎨 **Modern GUI**: Beautiful, intuitive interface built with Flet framework
- ⚡ **GPU Acceleration**: Automatic CUDA/MPS/CPU detection and optimization
- 🎛️ **Quality Control**: Comprehensive settings for maximum detail and quality
- 📦 **Batch Processing**: Process multiple frames in sequence
- 🔍 **Consistent Camera**: Same focal length for all frames (critical for 4DGS alignment)
- 🖼️ **Frame Range Selection**: Choose specific frame ranges to process
- 💾 **Auto-Conversion**: Automatic conversion to standard PLY format compatible with all viewers
- 🚀 **Hardware Optimization**: Automatic system detection and quality optimization
- 💼 **Portable EXE**: Standalone executable for Windows 10+ (no Python installation required)

## 📋 Requirements

### For Python Version

- **Python**: 3.11 or higher
- **GPU**: NVIDIA GPU with CUDA support (recommended) or Apple Silicon (MPS)
- **RAM**: 8GB+ (16GB+ recommended, 256GB for maximum quality)
- **VRAM**: 6GB+ for GPU acceleration (24GB RTX 4090 recommended)

### For EXE Version

- **OS**: Windows 10 or later
- **RAM**: 8GB+ (16GB+ recommended)
- **GPU**: NVIDIA GPU with CUDA (optional but recommended)
- **Disk Space**: ~5GB for application + space for results

## ⚠️ Important: License Notice

**Before using this application, please read**: [LICENSE_NOTICE.md](LICENSE_NOTICE.md)

The Apple SHARP model included in this application is licensed for **non-commercial research purposes only**. Commercial use is **prohibited**. 

**Summary:**
- ✅ **ALLOWED**: Research, education, open-source projects
- ❌ **PROHIBITED**: Commercial use, commercial products, paid services

See [License Section](#-license) below for complete details.

## 🚀 Quick Start

### Option 1: Portable EXE (Recommended for End Users)

1. Download `AndriiShramko_4DGS_Generator.exe` from [Releases](../../releases)
2. Run the EXE file (double-click)
3. On first launch, the application will download the SHARP model (~1.5GB) - this may take time
4. After model download, you're ready to use the application!

### Option 2: Python Installation (For Developers)

1. **Clone the repository:**
```bash
git clone https://github.com/AndriiShramko/4DGS-Video-Generator.git
cd 4DGS-Video-Generator
```

2. **Install dependencies:**
```bash
cd v02
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python video_app.py
```

Or use the provided scripts:
- **Windows**: `run_video_app.bat`
- **Linux/Mac**: `run_video_app.sh`

## 🎬 Usage Workflow

### Step 1: Select Video File

1. Click **"1. Select Video File"** button
2. Choose your video file (MP4, AVI, MOV, MKV, WEBM, M4V, FLV, WMV)
3. The application automatically analyzes the video:
   - Total frame count
   - FPS (frames per second)
   - Resolution
   - Duration

### Step 2: Select Output Folder

1. Click **"2. Select Output Folder"** button
2. Choose where to save generated PLY files
3. The application remembers this path for future sessions

### Step 3: Configure Settings

1. **Frame Range**: Set start and end frames (default: all frames)
   - Example: Process frames 0-99 for first 100 frames
2. **Focal Length**: Automatically estimated from video dimensions
   - **Important**: Same focal length is used for all frames (ensures consistent camera)
   - Can be manually adjusted if needed

### Step 4: Generate PLY Sequence

1. Click **"3. Generate PLY Sequence"** button
2. Watch detailed progress in real-time:
   - Progress bar shows overall completion
   - Detailed log shows status for each frame
3. After completion, a dialog appears with **"Open Folder"** button

## 📊 Output Format

### File Structure

```
{Output Folder}/
  └── {Video Name}/
      └── {YYYYMMDD_HHMMSS}/
          ├── frame_000000_Shramko_4DGS_apple-Sharp_Generator__standard.ply
          ├── frame_000001_Shramko_4DGS_apple-Sharp_Generator__standard.ply
          ├── frame_000002_Shramko_4DGS_apple-Sharp_Generator__standard.ply
          └── ...
```

### File Naming

Each generated PLY file includes:
- Frame number: `frame_XXXXXX`
- Copyright: `_Shramko_4DGS_apple-Sharp_Generator_`
- Format: `_standard.ply` (compatible with all 3DGS viewers)

### File Format

- **Standard PLY format**: Compatible with all 3DGS viewers
- **File size**: ~63 MB per frame (1,179,648 Gaussian elements)
- **Original SHARP format**: Automatically deleted after conversion

## 🎛️ Features in Detail

### Consistent Camera Parameters

**Critical Feature**: All frames use the **same focal length** (`f_px`). This ensures:
- Identical camera intrinsics across all frames
- Consistent 3D coordinate system
- Proper alignment of generated 4DGS objects

The focal length is:
- Auto-estimated from video dimensions (default FOV: 50°)
- Applied uniformly to all frames in the sequence
- Can be manually overridden if known

### Processing Resolution

- Fixed at **1536x1536** (SHARP model architecture requirement)
- Model uses patch-based encoding with patch_size=384
- Resolution cannot be changed without breaking checkpoint compatibility

### Frame Extraction

- Uses OpenCV for video processing
- Supports all common video formats
- Efficient frame-by-frame extraction
- Handles any video aspect ratio

### Progress Reporting

- Real-time progress bar
- Detailed log with timestamps
- Status for each frame (INFO, SUCCESS, WARNING, ERROR)
- Frame-by-frame generation progress

## 📁 Project Structure

```
4DGS-Video-Generator/
├── v02/                          # Main application directory
│   ├── video_app.py             # Main GUI application
│   ├── video_processor.py       # Video frame extraction module
│   ├── settings.py              # Settings management
│   ├── convert_sharp_ply.py     # PLY format converter
│   └── requirements.txt         # Python dependencies
├── ml-sharp/                     # Apple SHARP model (submodule)
├── sample-video/                 # Sample video for testing
│   └── na-avokado.mp4           # Test video file
├── build_exe.spec               # PyInstaller spec file
├── EXE_README.md                # EXE version documentation
├── DEVELOPER_GUIDE.md           # Developer documentation
└── README.md                    # This file
```

## 🔧 Advanced Usage

### Custom Settings

Edit `v02/settings.json` to customize default settings:

```json
{
  "device": "cuda",
  "processing_resolution": 1536,
  "low_pass_filter_eps": 0.001,
  "last_video_path": "path/to/last/video.mp4",
  "last_output_dir": "path/to/output/folder"
}
```

### Building EXE from Source

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed instructions on building the portable EXE.

## 🐛 Troubleshooting

### Video Not Opening

- Ensure video codec is supported (H.264, H.265, VP9, etc.)
- Check file path doesn't contain special characters
- Try converting video to MP4 with H.264 codec

### GPU Not Detected

If GPU is not detected:
1. Install PyTorch with CUDA support:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

2. Verify CUDA availability:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Out of Memory

If you encounter out-of-memory errors:
1. Process smaller frame ranges
2. Close other GPU-intensive applications
3. Use CPU mode (slower but uses less memory)

### EXE Not Starting

- Ensure Windows 10 or later
- Check antivirus (may block first launch)
- Run as administrator if needed
- Check that ~2GB free disk space available

## 📊 Performance

### Benchmarks (RTX 4090, 24GB VRAM)

- **Frame Processing Time**: ~2-3 seconds per frame
- **Output Size**: ~63 MB per PLY file
- **Gaussian Elements**: ~1,179,648 per frame
- **Video**: 450 frames, 30 FPS, 1950x1064 resolution
- **Total Processing Time**: ~15-20 minutes for 450 frames

### System Requirements

| Component | Minimum | Recommended | Optimal |
|-----------|---------|-------------|---------|
| GPU | 6GB VRAM | 12GB VRAM | 24GB VRAM |
| RAM | 8GB | 16GB | 256GB |
| CPU | 4 cores | 8 cores | 36 cores |
| Storage | 5GB | 10GB | 50GB+ |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

### Application Code

This application code (video_app.py, video_processor.py, etc.) is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Apple SHARP Model - IMPORTANT LICENSE RESTRICTIONS

**⚠️ CRITICAL: The Apple SHARP model has STRICT non-commercial license restrictions.**

The SHARP model (`ml-sharp/`) is licensed separately under the **Apple Machine Learning Research Model License**. See `ml-sharp/LICENSE_MODEL` for full details.

#### Key License Restrictions:

- ✅ **ALLOWED**: Non-commercial scientific research and academic development
- ✅ **ALLOWED**: Open-source research projects
- ✅ **ALLOWED**: Educational purposes

- ❌ **PROHIBITED**: Commercial exploitation
- ❌ **PROHIBITED**: Use in commercial products or services
- ❌ **PROHIBITED**: Product development for commercial use
- ❌ **PROHIBITED**: Selling services or products that use the SHARP model

#### What This Means:

**You CAN:**
- Use this application for research and educational purposes
- Develop open-source tools using the SHARP model
- Share research results

**You CANNOT:**
- Sell commercial products or services that use the SHARP model
- Use this in commercial projects for clients
- Offer paid services based on the SHARP model
- Include the SHARP model in commercial software

#### For Commercial Use:

If you need commercial usage rights:
1. Train your own model based on the methodology (without using SHARP weights)
2. Use alternative models with commercial licenses
3. Contact Apple directly for commercial licensing options

**Full license text**: See `ml-sharp/LICENSE_MODEL` for complete terms and conditions.

## 🙏 Acknowledgments

- **Apple ML Research** for the [SHARP model](https://github.com/apple/ml-sharp)
- **Flet** for the excellent GUI framework
- **PyTorch** for deep learning infrastructure
- **gsplat** for 3DGS rendering

## 📧 Contact

**Author**: Andrii Shramko  
**LinkedIn**: [@andrii-shramko](https://www.linkedin.com/in/andrii-shramko/)  
**Calendar**: [Schedule a meeting](https://calendar.app.google/K3mswrVbkAb8TTDF9)  
**GitHub**: [@AndriiShramko](https://github.com/AndriiShramko)

## 🔗 Related Projects

- [Apple ML-SHARP](https://github.com/apple/ml-sharp) - Original SHARP model
- [3D Gaussian Splatting](https://github.com/graphdeco-inria/gaussian-splatting) - Original 3DGS paper
- [Flet](https://flet.dev/) - Python GUI framework

---

**Made with ❤️ by Andrii Shramko**

© 2025 Andrii Shramko. All rights reserved.

