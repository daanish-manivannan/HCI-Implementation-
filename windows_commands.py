"""
windows_commands.py
───────────────────
Windows system-level operations:
  - Application launching (built-in and custom apps)
  - Windows navigation and control
  - File system operations
  - System utilities

Supports intelligent parsing of app names and parameters.
"""

import logging
import subprocess
import os
import sys
from typing import Dict, List, Optional
import winreg

# Setup logging
logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
))
logger.addHandler(_handler)
logger.setLevel(logging.INFO)


class WindowsCommandHandler:
    """
    Handles Windows system commands and app launching.
    """

    # Common Windows built-in apps and their executable paths/commands
    BUILTIN_APPS = {
        # Browsers
        "chrome": "chrome",
        "chromium": "chromium",
        "edge": "explorer",  # Edge
        "firefox": "firefox",
        "internet explorer": "iexplore",
        
        # Office
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
        "outlook": "outlook",
        "oneNote": "onenote",
        
        # System
        "notepad": "notepad",
        "calc": "calc",
        "paint": "mspaint",
        "file manager": "explorer",
        "settings": "ms-settings:",
        "task manager": "taskmgr",
        "command prompt": "cmd",
        "powershell": "powershell",
        "terminal": "wt",
        
        # Development
        "vscode": "code",
        "visual studio code": "code",
        "visual studio": "devenv",
        "python": "python",
        
        # Communication
        "teams": "teams",
        "discord": "discord",
        "telegram": "telegram",
        "zoom": "zoom",
        
        # Media
        "vlc": "vlc",
        "spotify": "spotify",
        "windows media player": "wmplayer",
        
        # Others
        "telegram": "telegram",
        "steam": "steam",
    }

    def __init__(self):
        logger.info("WindowsCommandHandler initialized")

    @staticmethod
    def launch_app(app_name: str, *args) -> str:
        """
        Launch a Windows application by name.
        
        Args:
            app_name: Name of app to launch (e.g., "chrome", "notepad", "word")
            *args: Optional arguments to pass to the app
        
        Returns:
            Status message
        """
        try:
            app_name_lower = app_name.lower().strip()
            logger.info("[Windows] >>> Attempting to launch app: '%s'", app_name_lower)
            
            # Check if it's a built-in app
            if app_name_lower in WindowsCommandHandler.BUILTIN_APPS:
                cmd = WindowsCommandHandler.BUILTIN_APPS[app_name_lower]
                logger.info("[Windows] >>> Found in BUILTIN_APPS: %s → %s", app_name, cmd)
                
                try:
                    if args:
                        subprocess.Popen([cmd] + list(args), shell=True)
                    else:
                        # Use shell=True to find executables in PATH
                        subprocess.Popen(cmd, shell=True, 
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                    logger.info("[Windows] >>> Successfully launched: %s", app_name)
                    return f"[OK] Launched {app_name}"
                except Exception as e:
                    logger.error("[Windows] >>> Failed with subprocess: %s", e)
                    # Fallback: try using os.startfile (Windows-specific)
                    try:
                        logger.info("[Windows] >>> Trying fallback with os.startfile...")
                        os.startfile(cmd)
                        logger.info("[Windows] >>> Successfully launched via os.startfile: %s", app_name)
                        return f"[OK] Launched {app_name}"
                    except Exception as e2:
                        logger.error("[Windows] >>> os.startfile also failed: %s", e2)
                        return f"[ERROR] Failed to launch {app_name}"
            
            # Try direct launch via shell
            try:
                logger.info("[Windows] >>> Attempting direct launch: '%s'", app_name_lower)
                if args:
                    subprocess.Popen(" ".join([app_name_lower] + list(args)), shell=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen(app_name_lower, shell=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                logger.info("[Windows] >>> Successfully launched via shell: %s", app_name)
                return f"[OK] Launched {app_name}"
            except Exception as e:
                logger.error("[Windows] >>> Direct launch failed: %s", e)
                return f"[ERROR] Failed to launch {app_name}: {str(e)}"
        except Exception as e:
            logger.error("[Windows] >>> Unexpected error: %s", e)
            return f"[ERROR] {str(e)}"

    @staticmethod
    def open_folder(path: str) -> str:
        """
        Open a folder in file explorer.
        
        Args:
            path: Folder path to open
        
        Returns:
            Status message
        """
        try:
            if os.path.isdir(path):
                subprocess.Popen(f'explorer "{path}"')
                logger.info("[Windows] Opened folder: %s", path)
                return f"📁 Opened: {path}"
            else:
                logger.warning("[Windows] Folder not found: %s", path)
                return f"❌ Folder not found: {path}"
        except Exception as e:
            logger.error("[Windows] Error opening folder: %s", e)
            return f"❌ Error: {str(e)}"

    @staticmethod
    def open_website(url: str) -> str:
        """
        Open a website in default browser.
        
        Args:
            url: Website URL
        
        Returns:
            Status message
        """
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            subprocess.Popen(url, shell=True)
            logger.info("[Windows] Opened URL: %s", url)
            return f"🌐 Opened: {url}"
        except Exception as e:
            logger.error("[Windows] Error opening URL: %s", e)
            return f"❌ Error: {str(e)}"

    @staticmethod
    def minimize_all() -> str:
        """Minimize all windows."""
        try:
            import pyautogui
            pyautogui.hotkey("win", "d")
            logger.info("[Windows] Minimized all windows")
            return "📉 All windows minimized"
        except Exception as e:
            logger.error("[Windows] Error minimizing windows: %s", e)
            return f"❌ Error: {str(e)}"

    @staticmethod
    def toggle_dark_mode() -> str:
        """Toggle Windows dark mode setting."""
        try:
            import winreg
            registry_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            registry_key = "AppsUseLightTheme"
            
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)
                value, _ = winreg.QueryValueEx(key, registry_key)
                winreg.CloseKey(key)
                
                # Toggle: 0 = dark, 1 = light
                new_value = 0 if value == 1 else 1
                
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, registry_key, 0, winreg.REG_DWORD, new_value)
                winreg.CloseKey(key)
                
                mode = "🌙 Dark Mode" if new_value == 0 else "☀️ Light Mode"
                logger.info("[Windows] Toggled dark mode: %s", mode)
                return f"Switched to {mode}"
            except Exception as e:
                logger.warning("[Windows] Could not toggle dark mode: %s", e)
                return "⚠️ Dark mode toggle not available"
        except Exception as e:
            logger.error("[Windows] Error: %s", e)
            return f"❌ Error: {str(e)}"

    @staticmethod
    def create_new_folder(name: str, location: str = None) -> str:
        """
        Create a new folder.
        
        Args:
            name: Folder name
            location: Parent folder path (default: Desktop)
        
        Returns:
            Status message
        """
        try:
            if location is None:
                location = os.path.expanduser("~/Desktop")
            
            folder_path = os.path.join(location, name)
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                logger.info("[Windows] Created folder: %s", folder_path)
                return f"📁 Created: {name}"
            else:
                logger.warning("[Windows] Folder already exists: %s", folder_path)
                return f"⚠️ Folder already exists: {name}"
        except Exception as e:
            logger.error("[Windows] Error creating folder: %s", e)
            return f"❌ Error: {str(e)}"

    @staticmethod
    def lock_screen() -> str:
        """Lock Windows screen."""
        try:
            import pyautogui
            pyautogui.hotkey("win", "l")
            logger.info("[Windows] Locked screen")
            return "🔒 Screen locked"
        except Exception as e:
            logger.error("[Windows] Error locking screen: %s", e)
            return f"❌ Error: {str(e)}"

    @staticmethod
    def open_calculator() -> str:
        """Open Windows Calculator."""
        try:
            subprocess.Popen("calc")
            logger.info("[Windows] Opened Calculator")
            return "🧮 Calculator opened"
        except Exception as e:
            logger.error("[Windows] Error opening calculator: %s", e)
            return f"❌ Error: {str(e)}"

    @staticmethod
    def open_settings(category: str = None) -> str:
        """
        Open Windows Settings.
        
        Args:
            category: Settings category (e.g., "sound", "display", "keyboard")
        
        Returns:
            Status message
        """
        try:
            if category:
                urls = {
                    "sound": "ms-settings:sound",
                    "display": "ms-settings:display",
                    "keyboard": "ms-settings:keyboard",
                    "mouse": "ms-settings:mouse",
                    "wifi": "ms-settings:network-wifi",
                    "bluetooth": "ms-settings:bluetooth",
                    "battery": "ms-settings:batterysaver",
                    "apps": "ms-settings:appsfeatures",
                }
                url = urls.get(category.lower(), "ms-settings:")
                subprocess.Popen(url, shell=True)
                logger.info("[Windows] Opened Settings: %s", category)
                return f"⚙️ Settings opened ({category})"
            else:
                subprocess.Popen("ms-settings:", shell=True)
                logger.info("[Windows] Opened Settings")
                return "⚙️ Settings opened"
        except Exception as e:
            logger.error("[Windows] Error opening settings: %s", e)
            return f"❌ Error: {str(e)}"

    @staticmethod
    def refresh_screen() -> str:
        """Refresh desktop/screen."""
        try:
            import pyautogui
            pyautogui.hotkey("f5")
            logger.info("[Windows] Refreshed screen")
            return "🔄 Screen refreshed"
        except Exception as e:
            logger.error("[Windows] Error refreshing screen: %s", e)
            return f"❌ Error: {str(e)}"
