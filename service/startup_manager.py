r"""
Mindfun — Startup Manager

Registers Mindfun to auto-start.
Currently uses Registry Run key (HKCU\Software\Microsoft\Windows\CurrentVersion\Run).
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
        return f'"{sys.executable}"'
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




# ─── Legacy Cleanup ─────────────────────────────────────────────────


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
    """Register startup methods and clean up legacy methods."""
    # Clean up legacy startup folder bat file if it exists
    unregister_startup_folder()
    
    results = {
        "registry": register_registry_startup(),
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



    return status
