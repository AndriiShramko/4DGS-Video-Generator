# Developer Guide - 4DGS Video Generator

This guide provides detailed information for developers who want to contribute, modify, or build the application from source.

## 📋 Table of Contents

1. [Development Setup](#development-setup)
2. [Project Architecture](#project-architecture)
3. [Building EXE](#building-exe)
4. [Code Structure](#code-structure)
5. [Testing](#testing)
6. [Contributing](#contributing)

## 🛠️ Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- CUDA Toolkit (for GPU support, optional)
- Visual Studio Build Tools (for building EXE on Windows)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/AndriiShramko/4DGS-Video-Generator.git
cd 4DGS-Video-Generator
```

2. **Initialize submodules:**
```bash
git submodule update --init --recursive
```

3. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies:**
```bash
cd v02
pip install -r requirements.txt
```

5. **Install PyInstaller (for building EXE):**
```bash
pip install pyinstaller
```

## 🏗️ Project Architecture

### Core Components

```
v02/
├── video_app.py              # Main GUI application (Flet)
├── video_processor.py         # Video frame extraction (OpenCV)
├── settings.py               # Settings management (JSON)
├── convert_sharp_ply.py       # PLY format conversion
└── requirements.txt          # Python dependencies

ml-sharp/                      # Apple SHARP model (Git submodule)
└── src/
    └── sharp/                # SHARP model implementation
```

### Data Flow

```
Video File
    ↓
VideoProcessor (extract frames)
    ↓
SHARP Model (generate 3DGS per frame)
    ↓
PLY Converter (convert to standard format)
    ↓
Output Directory (organized by video name and timestamp)
```

### Key Classes

#### `Video3DGSApp`
Main application class managing:
- GUI components (Flet)
- Video processing workflow
- Model loading and inference
- Progress reporting
- Settings persistence

#### `VideoProcessor`
Handles video operations:
- Frame extraction
- Video analysis (FPS, resolution, frame count)
- Focal length estimation

#### `SharpSettings`
Manages application settings:
- Model parameters
- Device selection
- Path persistence (video, output folder)

## 🔨 Building EXE

### Prerequisites

- PyInstaller installed
- All dependencies installed
- Windows 10+ (for Windows EXE)

### Build Process

1. **Prepare the environment:**
```bash
cd 4DGS-Video-Generator
pip install pyinstaller
```

2. **Build using spec file:**
```bash
pyinstaller build_exe.spec --clean --noconfirm
```

3. **Result:**
- EXE file: `dist/AndriiShramko_4DGS_Generator.exe`
- Size: ~2.8 GB (includes all dependencies)

### Spec File Configuration

The `build_exe.spec` file configures:
- **binaries**: Python DLL and runtime libraries
- **hiddenimports**: All required Python modules
- **datas**: Settings file and other data
- **console**: Set to `True` for debugging, `False` for release

### Troubleshooting EXE Build

**Issue: Missing DLL errors**
- Solution: Ensure all runtime DLLs are included in `binaries` list
- Check: Python DLL, VCRUNTIME DLLs, CUDA DLLs (if using GPU)

**Issue: Large EXE size**
- Expected: ~2.8 GB (includes PyTorch, OpenCV, all dependencies)
- Optimization: Use `--exclude-module` for unused modules

**Issue: EXE doesn't start**
- Check: Console mode enabled for debugging
- Verify: All DLLs are included
- Test: Run from command line to see errors

## 📂 Code Structure

### Main Application (`video_app.py`)

```python
class Video3DGSApp:
    def __init__(self, page):
        # Initialize UI and state
        
    def setup_page(self):
        # Configure Flet page settings
        
    def build_ui(self):
        # Create all UI components
        
    def select_video(self, e):
        # Handle video file selection
        
    def select_output_folder(self, e):
        # Handle output folder selection
        
    def load_model(self):
        # Load SHARP model
        
    def process_video(self):
        # Main processing loop
```

### Video Processor (`video_processor.py`)

```python
class VideoProcessor:
    def get_info(self):
        # Get video metadata
        
    def extract_frame(self, frame_number):
        # Extract single frame
        
    def extract_frames_range(self, start, end):
        # Extract frame range
        
    def estimate_focal_length(self, width, height):
        # Estimate focal length from dimensions
```

### Settings Management (`settings.py`)

```python
class SharpSettings:
    def __init__(self):
        # Initialize with defaults
        
    def load(self):
        # Load from JSON file
        
    def save(self):
        # Save to JSON file
        
    def apply_to_predictor_params(self, params):
        # Apply settings to SHARP model
```

## 🧪 Testing

### Unit Tests

Create test files in `tests/` directory:

```bash
python -m pytest tests/
```

### Manual Testing

1. **Test video loading:**
   - Select various video formats
   - Verify frame count detection
   - Check focal length estimation

2. **Test frame processing:**
   - Process small frame range (5-10 frames)
   - Verify PLY file generation
   - Check file naming (copyright included)

3. **Test settings persistence:**
   - Select video and output folder
   - Close and reopen application
   - Verify paths are remembered

4. **Test error handling:**
   - Invalid video format
   - Invalid frame range
   - Missing output folder

### Sample Video

Use `sample-video/na-avokado.mp4` for testing:
- 450 frames
- 30 FPS
- 1950x1064 resolution
- ~15 seconds duration

## 🔄 Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes
4. Test thoroughly
5. Commit: `git commit -m "Add amazing feature"`
6. Push: `git push origin feature/amazing-feature`
7. Open Pull Request

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where possible
- Add docstrings to all functions
- Keep functions focused and small

### Commit Messages

Use clear, descriptive commit messages:
- `Add: Feature description`
- `Fix: Bug description`
- `Update: Component description`
- `Refactor: Code description`

## 🐛 Debugging

### Enable Console Mode

In `build_exe.spec`, set:
```python
console=True,  # Show console window
```

### Logging

The application uses detailed logging:
- INFO: General information
- SUCCESS: Successful operations
- WARNING: Warnings
- ERROR: Errors
- PROGRESS: Processing progress

### Common Issues

**Model loading fails:**
- Check internet connection (model downloads on first run)
- Verify disk space (~2GB for model)
- Check CUDA availability (if using GPU)

**Video processing errors:**
- Verify video codec support
- Check OpenCV installation
- Ensure sufficient RAM/VRAM

**EXE build errors:**
- Check all dependencies installed
- Verify PyInstaller version compatibility
- Review spec file configuration

## 📚 Additional Resources

- [Flet Documentation](https://flet.dev/docs/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)
- [SHARP Model](https://github.com/apple/ml-sharp)
- [OpenCV Documentation](https://docs.opencv.org/)

## 📝 License

See [LICENSE](LICENSE) file for details.

---

**Happy Coding! 🚀**

