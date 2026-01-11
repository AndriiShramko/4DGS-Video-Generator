# Fixing SSL Certificate Error (Current Version)

## Problem

If you see this error when starting the application:

```
Error: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain>
```

This happens because the automatic model download fails due to SSL certificate verification issues (often caused by corporate firewalls, proxies, or security software).

## Solution: Manual Model Download

Follow these steps to manually download and install the SHARP model:

### Step 1: Download the Model

1. **Open your web browser** and download the model file directly:
   - **URL**: `https://ml-site.cdn-apple.com/models/sharp/sharp_2572gikvuh.pt`
   - **File size**: ~1.5 GB
   - **File name**: `sharp_2572gikvuh.pt`

2. **Save the file** to your Downloads folder or any accessible location.

### Step 2: Locate the Checkpoints Folder

The application expects the model file to be in the PyTorch hub cache folder:

**Windows:**
```
C:\Users\<YOUR_USERNAME>\.cache\torch\hub\checkpoints\
```

**macOS/Linux:**
```
~/.cache/torch/hub/checkpoints/
```

**Note**: Replace `<YOUR_USERNAME>` with your actual Windows username.

### Step 3: Create the Folder (if needed)

If the `checkpoints` folder doesn't exist:

1. Open File Explorer (Windows) or Finder (macOS)
2. Navigate to:
   - **Windows**: `C:\Users\<YOUR_USERNAME>\.cache\torch\hub\`
   - **macOS/Linux**: `~/.cache/torch/hub/`
3. Create a new folder named `checkpoints` if it doesn't exist
4. If `.cache` folder doesn't exist, create the entire path: `.cache\torch\hub\checkpoints\`

**Quick Windows Method:**
1. Press `Win + R`
2. Type: `%USERPROFILE%\.cache\torch\hub\checkpoints`
3. Press Enter (Windows will create folders if needed)
4. If folder doesn't open, create it manually in File Explorer

### Step 4: Copy the Model File

1. **Copy** the downloaded `sharp_2572gikvuh.pt` file
2. **Paste** it into the `checkpoints` folder
3. **Verify** the file is there:
   - Full path should be: `C:\Users\<YOUR_USERNAME>\.cache\torch\hub\checkpoints\sharp_2572gikvuh.pt`
   - File size should be ~1.5 GB

### Step 5: Restart the Application

1. Close the application completely
2. Start it again
3. The application will now find the model in the cache folder and load it automatically

## Verification

After following these steps:

1. **First launch**: The application should load the model from the cache folder (no download attempt)
2. **Check the Log**: You should see "Loading model checkpoint..." and "Model loaded successfully" instead of SSL errors
3. **No more errors**: The SSL certificate error should be gone

## Alternative: Direct File Path (Future Version)

A future version of the application will allow you to specify the model file path directly in the settings, eliminating the need to use the cache folder.

## Troubleshooting

### Model Still Not Found

1. **Check the file name**: Must be exactly `sharp_2572gikvuh.pt` (case-sensitive on Linux/macOS)
2. **Check the path**: Verify the full path matches exactly:
   - Windows: `C:\Users\<USERNAME>\.cache\torch\hub\checkpoints\sharp_2572gikvuh.pt`
   - macOS/Linux: `~/.cache/torch/hub/checkpoints/sharp_2572gikvuh.pt`
3. **File permissions**: Ensure the file is not read-only or locked
4. **Disk space**: Ensure you have enough free space (~2 GB recommended)

### Download Fails in Browser

If the browser download also fails:

1. **Try a different browser** (Chrome, Firefox, Edge)
2. **Disable browser extensions** temporarily
3. **Check firewall/proxy settings**
4. **Use a VPN** if behind a restrictive network
5. **Try downloading from a different network** (mobile hotspot, etc.)

### Still Having Issues?

1. Check the application log for detailed error messages
2. Verify Python/PyTorch installation
3. Ensure you have internet connectivity
4. Contact support with the full error message from the log

## Technical Details

- **Model URL**: `https://ml-site.cdn-apple.com/models/sharp/sharp_2572gikvuh.pt`
- **Expected cache location**: PyTorch hub cache (`~/.cache/torch/hub/checkpoints/` on Unix, `%USERPROFILE%\.cache\torch\hub\checkpoints\` on Windows)
- **File format**: PyTorch state dictionary (`.pt` file)
- **File size**: ~1.5 GB (1,574,912,000 bytes)

---

**Last Updated**: January 2025  
**Applies to**: Versions before SSL certificate fix
