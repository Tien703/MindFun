"""
Mindfun — Process Controller

Uses ctypes to call Windows NT API (NtSuspendProcess / NtResumeProcess)
to suspend/resume entire process trees. This is the core mechanism that
freezes games while the lockscreen countdown runs.

Technical notes:
- NtSuspendProcess/NtResumeProcess are undocumented but stable from XP to Win11
- We use PROCESS_SUSPEND_RESUME (0x0800) for minimum privilege
- No memory reading/writing — safe from anti-cheat detection
"""

import ctypes
from ctypes import wintypes
import logging

import psutil

logger = logging.getLogger("mindfun.process_controller")

# ─── Windows API Setup ───────────────────────────────────────────────

try:
    _ntdll = ctypes.WinDLL("ntdll")
    _kernel32 = ctypes.windll.kernel32

    # Process access rights
    PROCESS_SUSPEND_RESUME = 0x0800
    PROCESS_TERMINATE = 0x0001
    PROCESS_ALL_ACCESS = 0x1F0FFF

    # Set up NtSuspendProcess
    _NtSuspendProcess = _ntdll.NtSuspendProcess
    _NtSuspendProcess.argtypes = (wintypes.HANDLE,)
    _NtSuspendProcess.restype = wintypes.LONG

    # Set up NtResumeProcess
    _NtResumeProcess = _ntdll.NtResumeProcess
    _NtResumeProcess.argtypes = (wintypes.HANDLE,)
    _NtResumeProcess.restype = wintypes.LONG

    # Set up OpenProcess
    _OpenProcess = _kernel32.OpenProcess
    _OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    _OpenProcess.restype = wintypes.HANDLE

    # Set up CloseHandle
    _CloseHandle = _kernel32.CloseHandle
    _CloseHandle.argtypes = (wintypes.HANDLE,)
    _CloseHandle.restype = wintypes.BOOL

    _API_AVAILABLE = True
except (OSError, AttributeError) as e:
    logger.warning("Windows NT API not available (not on Windows?): %s", e)
    _API_AVAILABLE = False


# ─── Internal helpers ────────────────────────────────────────────────

def _suspend_single(pid: int) -> bool:
    """Suspend a single process by PID. Returns True on success."""
    if not _API_AVAILABLE:
        logger.warning("Cannot suspend PID %d: API not available", pid)
        return False

    handle = _OpenProcess(PROCESS_SUSPEND_RESUME, False, pid)
    if not handle:
        logger.warning("Cannot open process PID %d for suspend (access denied or not found)", pid)
        return False

    try:
        status = _NtSuspendProcess(handle)
        if status < 0:
            logger.warning("NtSuspendProcess failed for PID %d, NTSTATUS=0x%08X", pid, status & 0xFFFFFFFF)
            return False
        logger.info("Suspended PID %d", pid)
        return True
    finally:
        _CloseHandle(handle)


def _resume_single(pid: int) -> bool:
    """Resume a single process by PID. Returns True on success."""
    if not _API_AVAILABLE:
        logger.warning("Cannot resume PID %d: API not available", pid)
        return False

    handle = _OpenProcess(PROCESS_SUSPEND_RESUME, False, pid)
    if not handle:
        logger.warning("Cannot open process PID %d for resume (access denied or not found)", pid)
        return False

    try:
        status = _NtResumeProcess(handle)
        if status < 0:
            logger.warning("NtResumeProcess failed for PID %d, NTSTATUS=0x%08X", pid, status & 0xFFFFFFFF)
            return False
        logger.info("Resumed PID %d", pid)
        return True
    finally:
        _CloseHandle(handle)


# ─── Public API ──────────────────────────────────────────────────────

def suspend_process_tree(pid: int):
    """
    Suspend the target process and all its child processes.
    Children are suspended FIRST, then the parent — prevents race conditions
    where the parent spawns new children while we're suspending.
    """
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        # Suspend children first, parent last
        for child in children:
            try:
                _suspend_single(child.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        _suspend_single(pid)
        logger.info("Suspended process tree rooted at PID %d (%d children)", pid, len(children))

    except psutil.NoSuchProcess:
        logger.warning("Process PID %d no longer exists", pid)
    except psutil.AccessDenied:
        logger.warning("Access denied to process PID %d", pid)


def resume_process_tree(pid: int):
    """
    Resume the target process and all its child processes.
    Parent is resumed FIRST, then children — ensures parent can manage children.
    """
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        # Resume parent first, children after
        _resume_single(pid)
        for child in children:
            try:
                _resume_single(child.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        logger.info("Resumed process tree rooted at PID %d (%d children)", pid, len(children))

    except psutil.NoSuchProcess:
        logger.warning("Process PID %d no longer exists", pid)
    except psutil.AccessDenied:
        logger.warning("Access denied to process PID %d", pid)


def kill_process_tree(pid: int):
    """
    Kill the target process and all its child processes.
    Used when user chooses "QUIT" or Hardcore mode kills game at night.
    Children are killed first, then parent.
    """
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        for child in children:
            try:
                child.kill()
                logger.info("Killed child PID %d", child.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        parent.kill()
        logger.info("Killed parent PID %d (tree of %d children)", pid, len(children))

    except psutil.NoSuchProcess:
        logger.warning("Process PID %d no longer exists", pid)
    except psutil.AccessDenied:
        logger.warning("Access denied to kill PID %d", pid)


def find_process_by_name(name: str) -> list[psutil.Process]:
    """
    Find all running processes matching the given executable name (case-insensitive).
    Returns a list of psutil.Process objects.
    """
    matches = []
    name_lower = name.lower()
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == name_lower:
                matches.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return matches


def is_process_running(pid: int) -> bool:
    """Check if a process with the given PID is still running."""
    try:
        proc = psutil.Process(pid)
        return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
