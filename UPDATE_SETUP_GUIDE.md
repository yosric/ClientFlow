# Remote App Update System - Setup Guide

## What Has Been Done ✅

### Files Created:
1. **update_manager.py** - Core update checking and downloading functionality

### Files Modified:
1. **mainv2.py** - Added update button + handlers
2. **requirements.txt** - Added `requests` package
3. **param.py** - Already configured with update URLs

---

## Setup Instructions for Remote Updates

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

Or specifically:
```powershell
pip install requests>=2.28.0
```

### Step 2: Prepare Your GitHub Release
1. Build your app as .exe using PyInstaller:
```powershell
pyinstaller ClientFlowApp.spec
```

2. Upload the .exe to GitHub Releases:
   - Go to: https://github.com/YosriSaadi/ClientFlow/releases
   - Create new release with tag (e.g., `v1.3.2`)
   - Upload the `.exe` file
   - Copy the download URL

### Step 3: Update Version Configuration

Edit `param.py` and update:
```python
APP_VERSION="1.3.2"  # Your new version number
APP_URL="https://github.com/YosriSaadi/ClientFlow/releases/download/v1.3.2/ClientFlowApp.exe"
UPDATE_JSON_URL="https://raw.githubusercontent.com/YosriSaadi/ClientFlow/main/version.json"
```

Edit `version.json`:
```json
{
  "version": "1.3.2",
  "url": "https://github.com/YosriSaadi/ClientFlow/releases/download/v1.3.2/ClientFlowApp.exe",
  "notes": "Your update notes here"
}
```

### Step 4: Commit and Push
```powershell
git add param.py version.json
git commit -m "Release v1.3.2"
git push
```

---

## How It Works for Your Clients

### User Flow:
1. **Click "⬇️ Check for Updates"** button in top-right corner
2. App checks `version.json` from GitHub
3. If newer version available → Shows dialog with notes
4. User clicks "Yes" → Downloads .exe in background
5. Shows progress: "📥 Downloading... 50%"
6. Once complete → "Update Ready" dialog
7. App restarts & installer runs automatically

---

## UI Button Location
The update button appears in the top toolbar next to the "ℹ À Propos" button:
- **Position:** Top-right of main window
- **Icon:** ⬇️ Check for Updates
- **States:**
  - ⬇️ Check for Updates (idle)
  - ⏳ Checking... (checking for updates)
  - 📥 Downloading... XX% (downloading)

---

## Key Features

✅ **Background Checking** - Uses threading, doesn't block UI
✅ **Progress Tracking** - Shows download percentage
✅ **Error Handling** - User-friendly error messages
✅ **Automatic Installation** - Downloads then runs installer
✅ **Semantic Versioning** - Compares versions properly (1.3.2 > 1.3.1)

---

## Troubleshooting

### "Update check failed" error
- Check internet connection
- Verify GitHub URLs are accessible
- Check `UPDATE_JSON_URL` in param.py

### "Download failed" error  
- Verify release URL is correct
- Check file size (shouldn't be > 500MB)
- Check disk space

### Version comparison not working
- Ensure versions use semantic versioning: `x.y.z`
- Both APP_VERSION and version.json must match exactly

---

## Testing Before Release

1. Change APP_VERSION to 0.0.1 and version.json to 1.0.0
2. Click "Check for Updates" - should find update
3. Accept the download
4. Verify .exe paths are valid

---

## Next Steps for Your App

1. **Customize Update Notes** - Update `version.json` notes field
2. **Create Release** - Build and upload .exe to GitHub
3. **Update Configuration** - Modify `param.py` with new version
4. **Test with Clients** - Have a test client try the update flow
5. **Monitor** - Track if updates are being applied successfully

---

**All code integrated into mainv2.py ✅**

The update system is fully functional and ready to use!
