r"""
Mindfun — Startup Manager

Registers Mindfun to auto-start using three independent methods
for maximum persistence:
1. Registry Run key (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)
2. Task Scheduler (at logon)
3. Startup folder shortcut

The user would need to disable all three to prevent auto-start,
adding significant friction against impulse bypass.
"""

import logging
import os
import sys
import subprocess
from pathlib import Path

logger = logging.getLogger("mindfun.startup_manager")


def _get_pythonw_executable() -> str:
    """Get the path to pythonw.exe for running without a console in dev mode."""
    exe = sys.executable
    if exe.lower().endswith("python.exe"):
        return exe[:-10] + "pythonw.exe"
    return exe


def _get_exe_path() -> str:
    """Get the path to the Mindfun executable."""
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        # Dev mode: use pythonw + main.py
        return f'"{_get_pythonw_executable()}" "{Path(__file__).resolve().parent.parent / "main.py"}"'





# ─── Method 1: Registry Run Key ─────────────────────────────────────

def register_registry_startup():
    """Add Mindfun to the Windows Registry Run key."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "Mindfun", 0, winreg.REG_SZ, _get_exe_path())
        winreg.CloseKey(key)
        logger.info("Registered in Registry Run key")
        return True
    except Exception as e:
        logger.error("Failed to register Registry startup: %s", e)
        return False


def unregister_registry_startup():
    """Remove Mindfun from the Windows Registry Run key."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            winreg.DeleteValue(key, "Mindfun")
        except FileNotFoundError:
            pass

        winreg.CloseKey(key)
        logger.info("Unregistered from Registry Run key")
    except Exception as e:
        logger.error("Failed to unregister Registry startup: %s", e)


# ─── Method 2: Task Scheduler ───────────────────────────────────────




# ─── Method 3: Startup Folder ───────────────────────────────────────

def register_startup_folder():
    """Create a shortcut in the user's Startup folder."""
    try:
        startup_dir = Path(os.environ.get("APPDATA", "")) / \
            r"Microsoft\Windows\Start Menu\Programs\Startup"
        shortcut_path = startup_dir / "Mindfun.bat"

        # Write a simple batch file that starts Mindfun silently
        exe = _get_exe_path()
        with open(shortcut_path, "w") as f:
            f.write(f'@echo off\nstart /min "" {exe}\n')

        logger.info("Created startup folder shortcut: %s", shortcut_path)
        return True
    except Exception as e:
        logger.error("Failed to create startup folder shortcut: %s", e)
        return False


def unregister_startup_folder():
    """Remove the startup folder shortcut."""
    try:
        startup_dir = Path(os.environ.get("APPDATA", "")) / \
            r"Microsoft\Windows\Start Menu\Programs\Startup"
        shortcut_path = startup_dir / "Mindfun.bat"
        shortcut_path.unlink(missing_ok=True)
        logger.info("Removed startup folder shortcut")
    except Exception as e:
        logger.error("Failed to remove startup folder shortcut: %s", e)


# ─── Combined Operations ────────────────────────────────────────────

def register_all_startup():
    """Register all three startup methods."""
    results = {
        "registry": register_registry_startup(),
        "startup_folder": register_startup_folder(),
    }
    logger.info("Startup registration results: %s", results)
    return results


def unregister_all_startup():
    """Remove all startup registrations (for uninstall)."""
    unregister_registry_startup()
    unregister_startup_folder()
    logger.info("All startup registrations removed")


def check_startup_status() -> dict[str, bool]:
    """Check which startup methods are currently registered."""
    status = {}

    # Check registry
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        )
        try:
            winreg.QueryValueEx(key, "Mindfun")
            status["registry"] = True
        except FileNotFoundError:
            status["registry"] = False
        winreg.CloseKey(key)
    except Exception:
        status["registry"] = False



    # Check Startup folder
    startup_dir = Path(os.environ.get("APPDATA", "")) / \
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    status["startup_folder"] = (startup_dir / "Mindfun.bat").exists()

    return status
