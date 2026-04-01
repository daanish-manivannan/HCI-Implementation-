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
        "google chrome": "chrome",
        "chromium": "chromium",
        "edge": "msedge",
        "microsoft edge": "msedge",
        "firefox": "firefox",
        "internet explorer": "iexplore",

        # Office
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
        "outlook": "outlook",
        "onenote": "onenote",

        # System
        "notepad": "notepad",
        "calc": "calc",
        "calculator": "calc",
        "paint": "mspaint",
        "file manager": "explorer",
        "file explorer": "explorer",
        "explorer": "explorer",
        "task manager": "taskmgr",
        "command prompt": "cmd",
        "powershell": "powershell",
        "terminal": "wt",

        # Development — voice SR often hears "vs code" or "visual code"
        "vscode": "code",
        "vs code": "code",
        "visual code": "code",
        "visual studio code": "code",
        "visual studio": "devenv",
        "notepad++": "notepad++",
        "notepad plus plus": "notepad++",
        "sublime": "subl",
        "sublime text": "subl",
        "python": "python",

        # Communication
        "teams": "teams",
        "discord": "discord",
        "telegram": "telegram",
        "zoom": "zoom",
        "whatsapp": "whatsapp",

        # Media
        "vlc": "vlc",
        "spotify": "spotify",
        "windows media player": "wmplayer",

        # Others
        "steam": "steam",
        "github": "github",
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
        import shutil
        try:
            app_name_lower = app_name.lower().strip()
            logger.info("[Windows] >>> Attempting to launch app: '%s'", app_name_lower)

            # Check if it's a built-in app
            if app_name_lower in WindowsCommandHandler.BUILTIN_APPS:
                cmd = WindowsCommandHandler.BUILTIN_APPS[app_name_lower]
                logger.info("[Windows] >>> Found in BUILTIN_APPS: %s -> %s", app_name, cmd)

                # Strategy 1: use cmd /c (handles .cmd wrappers like code.cmd)
                try:
                    if args:
                        full = f'cmd /c "{cmd}" ' + ' '.join(f'"{a}"' for a in args)
                    else:
                        full = f'cmd /c "{cmd}"'
                    subprocess.Popen(full, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    logger.info("[Windows] >>> Successfully launched: %s", app_name)
                    return f"[OK] Launched {app_name}"
                except Exception as e:
                    logger.debug("[Windows] >>> cmd /c failed: %s", e)

                # Strategy 2: os.startfile (handles UWP/store apps)
                try:
                    os.startfile(cmd)
                    logger.info("[Windows] >>> Launched via os.startfile: %s", app_name)
                    return f"[OK] Launched {app_name}"
                except Exception as e2:
                    logger.debug("[Windows] >>> os.startfile failed: %s", e2)
                    return f"[ERROR] Failed to launch {app_name}"

            # Not in BUILTIN_APPS - try direct launch
            logger.info("[Windows] >>> Attempting direct launch: '%s'", app_name_lower)
            # Strategy 1: if it looks like it could be an executable on PATH
            if shutil.which(app_name_lower):
                subprocess.Popen(f'cmd /c "{app_name_lower}"', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info("[Windows] >>> Launched via PATH: %s", app_name)
                return f"[OK] Launched {app_name}"

            # Strategy 2: Windows Start menu search via shell
            try:
                os.startfile(app_name_lower)
                logger.info("[Windows] >>> Launched via os.startfile: %s", app_name)
                return f"[OK] Launched {app_name}"
            except Exception:
                pass

            logger.warning("[Windows] >>> Could not find app: '%s'", app_name_lower)
            return f"[ERROR] App not found: {app_name}"
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
        """Open a website in default browser."""
        try:
            import webbrowser
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            webbrowser.open(url)
            logger.info("[Windows] Opened URL: %s", url)
            return f"Opened: {url}"
        except Exception as e:
            logger.error("[Windows] Error opening URL: %s", e)
            return f"Error: {str(e)}"

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
        """Open Windows Settings.  Uses os.startfile for ms-settings: URI."""
        try:
            urls = {
                "sound": "ms-settings:sound",
                "display": "ms-settings:display",
                "keyboard": "ms-settings:keyboard",
                "mouse": "ms-settings:mouse",
                "wifi": "ms-settings:network-wifi",
                "bluetooth": "ms-settings:bluetooth",
                "battery": "ms-settings:batterysaver",
                "apps": "ms-settings:appsfeatures",
                "personalization": "ms-settings:personalization",
                "accounts": "ms-settings:yourinfo",
                "updates": "ms-settings:windowsupdate",
                "privacy": "ms-settings:privacy",
                "network": "ms-settings:network",
                "update": "ms-settings:windowsupdate",
            }
            if category:
                # Extract the last word as the real category key
                cat_key = category.strip().lower().split()[-1]
                url = urls.get(cat_key, "ms-settings:")
            else:
                url = "ms-settings:"
            os.startfile(url)
            logger.info("[Windows] Opened Settings: %s -> %s", category or "main", url)
            return f"Settings opened ({category or 'main'})"
        except Exception as e:
            logger.error("[Windows] Error opening settings: %s", e)
            return f"Error: {str(e)}"

    @staticmethod
    def refresh_screen() -> str:
        """Refresh desktop/screen."""
        try:
            import pyautogui
            pyautogui.hotkey("f5")
            logger.info("[Windows] Refreshed screen")
            return "Screen refreshed"
        except Exception as e:
            logger.error("[Windows] Error refreshing screen: %s", e)
            return f"Error: {str(e)}"

    # ── New system commands ──────────────────────────────────────────────

    @staticmethod
    def volume_up(step: int = 2) -> str:
        """Increase system volume."""
        try:
            import pyautogui
            for _ in range(step):
                pyautogui.hotkey("volumeup")
            logger.info("[Windows] Volume up x%d", step)
            return f"Volume up (x{step})"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def volume_down(step: int = 2) -> str:
        """Decrease system volume."""
        try:
            import pyautogui
            for _ in range(step):
                pyautogui.hotkey("volumedown")
            logger.info("[Windows] Volume down x%d", step)
            return f"Volume down (x{step})"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def volume_mute() -> str:
        """Toggle system mute."""
        try:
            import pyautogui
            pyautogui.hotkey("volumemute")
            logger.info("[Windows] Volume mute toggled")
            return "Volume mute toggled"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def brightness_up() -> str:
        """Increase screen brightness."""
        try:
            # WMI brightness control
            subprocess.run(
                ['powershell', '-Command',
                 '(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, [math]::Min(100, (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness + 10))'],
                capture_output=True, timeout=5
            )
            logger.info("[Windows] Brightness up")
            return "Brightness increased"
        except Exception as e:
            logger.warning("[Windows] Brightness control failed: %s", e)
            return f"Brightness control not available: {e}"

    @staticmethod
    def brightness_down() -> str:
        """Decrease screen brightness."""
        try:
            subprocess.run(
                ['powershell', '-Command',
                 '(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, [math]::Max(0, (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness - 10))'],
                capture_output=True, timeout=5
            )
            logger.info("[Windows] Brightness down")
            return "Brightness decreased"
        except Exception as e:
            logger.warning("[Windows] Brightness control failed: %s", e)
            return f"Brightness control not available: {e}"

    @staticmethod
    def toggle_bluetooth() -> str:
        """Open Bluetooth settings (toggle requires admin)."""
        try:
            os.startfile("ms-settings:bluetooth")
            logger.info("[Windows] Opened Bluetooth settings")
            return "Bluetooth settings opened"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def maximize_all() -> str:
        """Restore / show all windows (opposite of minimize all)."""
        try:
            import pyautogui
            pyautogui.hotkey("win", "d")
            logger.info("[Windows] Restored all windows")
            return "All windows restored"
        except Exception as e:
            return f"Error: {e}"
