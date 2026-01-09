# EXE Version - Quick Start Guide

## 📦 Portable Executable

The EXE version is a standalone application that requires **no Python installation**. It includes all dependencies and can run on any Windows 10+ computer.

## 🚀 Installation

1. Download `AndriiShramko_4DGS_Generator.exe` from [Releases](../../releases)
2. Place the EXE file in any folder
3. Double-click to run

## ⚙️ First Launch

On first launch, the application will:
1. Extract temporary files (may take 1-2 minutes)
2. Download the SHARP model checkpoint (~1.5 GB) - **requires internet connection**
3. Save the model locally for future use

**Note**: First launch may take 10-15 minutes depending on your internet speed.

## 📋 System Requirements

- **OS**: Windows 10 or later (64-bit)
- **RAM**: 8GB minimum, 16GB+ recommended
- **GPU**: NVIDIA GPU with CUDA (optional but recommended)
- **Disk Space**: ~5GB for application + space for results
- **Internet**: Required for first launch (model download)

## 🎬 Usage

See [README.md](README.md) for detailed usage instructions.

## 🔧 Settings

Settings are saved in `settings.json` in the same folder as the EXE:
- Last selected video path
- Last selected output folder
- Model parameters

## 🐛 Troubleshooting

### EXE Won't Start

1. **Check Windows version**: Requires Windows 10 or later
2. **Antivirus**: May block first launch - add exception if needed
3. **Run as Administrator**: Try right-click → Run as administrator
4. **Disk space**: Ensure ~5GB free space available

### Model Download Fails

1. **Internet connection**: Check your connection
2. **Firewall**: May block download - check firewall settings
3. **Disk space**: Ensure ~2GB free for model
4. **Retry**: Close and reopen the application

### Slow Performance

1. **Use GPU**: Ensure CUDA is available (NVIDIA GPU)
2. **Close other apps**: Free up RAM and GPU memory
3. **Process fewer frames**: Reduce frame range

## 📝 Notes

- The EXE is portable - you can move it to any folder
- Settings are saved relative to EXE location
- Model is cached after first download
- All generated files include copyright in filename

---

**For developers**: See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for building EXE from source.

