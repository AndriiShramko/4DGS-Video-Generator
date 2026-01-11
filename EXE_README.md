# EXE Version - Quick Start Guide

## 📦 Portable Executable

The EXE version is a standalone application that requires **no Python installation**. It includes all dependencies and can run on any Windows 10+ computer.

## 🚀 Installation

**⚠️ IMPORTANT: You need BOTH files!**

1. Download **both files** from [Releases](../../releases):
   - `AndriiShramko_4DGS_Generator.exe` (~3.7 GB)
   - `sharp_2572gikvuh.pt` (~2.6 GB)

2. **Place both files in the SAME folder**

3. Double-click `AndriiShramko_4DGS_Generator.exe` to run

## ⚙️ First Launch

On first launch, the application will:
1. Extract temporary files (may take 1-2 minutes)
2. Automatically find the model file in the same folder
3. Load the model and be ready to use

**Note**: The model is NOT included in the EXE. Both files must be in the same directory.

See [DISTRIBUTION_INSTRUCTIONS.md](DISTRIBUTION_INSTRUCTIONS.md) for complete setup guide.

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

### Model Download Fails / SSL Certificate Error

**If you see SSL certificate error:**

1. **Download model manually:**
   - URL: `https://ml-site.cdn-apple.com/models/sharp/sharp_2572gikvuh.pt`
   - Save to: `C:\Users\<YOUR_USERNAME>\.cache\torch\hub\checkpoints\sharp_2572gikvuh.pt`
   - Create folder if needed: `.cache\torch\hub\checkpoints\`

2. **Restart application**

**Detailed fix:** See [SSL_CERTIFICATE_FIX.md](SSL_CERTIFICATE_FIX.md)

**Other download issues:**

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

