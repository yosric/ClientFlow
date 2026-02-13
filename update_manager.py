import os
import json
import requests
import subprocess
import tempfile
import shutil
from PySide6.QtCore import QThread, Signal
from param import UPDATE_JSON_URL, APP_VERSION

class UpdateChecker(QThread):
    """Check for app updates in background thread"""
    update_available = Signal(dict)  # Emits {'version': str, 'url': str, 'notes': str}
    check_error = Signal(str)  # Emits error message
    
    def run(self):
        try:
            response = requests.get(UPDATE_JSON_URL, timeout=5)
            response.raise_for_status()
            remote_version = response.json()
            
            # Compare versions
            if self.is_newer_version(remote_version.get('version'), APP_VERSION):
                self.update_available.emit(remote_version)
            
        except Exception as e:
            self.check_error.emit(f"Update check failed: {str(e)}")
    
    @staticmethod
    def is_newer_version(remote_version, current_version):
        """Compare semantic versions"""
        try:
            remote_parts = [int(x) for x in remote_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            for r, c in zip(remote_parts, current_parts):
                if r > c:
                    return True
                elif r < c:
                    return False
            return False
        except:
            return False


class AppUpdater(QThread):
    """Download and install app update"""
    progress = Signal(int)  # Progress percentage
    download_complete = Signal(str)  # Path to downloaded file
    update_error = Signal(str)  # Error message
    
    def __init__(self, download_url, output_path=None):
        super().__init__()
        self.download_url = download_url
        self.output_path = output_path or os.path.join(tempfile.gettempdir(), "app_update.exe")
    
    def run(self):
        try:
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(self.output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress.emit(progress)
            
            self.download_complete.emit(self.output_path)
            
        except Exception as e:
            self.update_error.emit(f"Download failed: {str(e)}")


def install_update(exe_path):
    """Launch the installer and restart app"""
    try:
        # Run the installer
        subprocess.Popen([exe_path])
        # Close current app
        os.execl(exe_path, exe_path)
    except Exception as e:
        raise Exception(f"Installation failed: {str(e)}")
