"""
Mindfun — Process Controller

Provides utilities for monitoring process state.
"""

import logging
import psutil

logger = logging.getLogger("mindfun.process_controller")


def is_process_running(pid: int) -> bool:
    """Check if a process with the given PID is still running."""
    try:
        proc = psutil.Process(pid)
        return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
