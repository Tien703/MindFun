"""
Mindfun — Game Detector

Polls running processes every 3 seconds and detects games from the configured list.
When a new game is detected (not yet whitelisted), it triggers the callback which
shows the lockscreen popup.

Design notes:
- Uses psutil.process_iter() for safe, low-overhead process enumeration
- 3-second polling interval avoids anti-cheat flags (no hooks, no events)
- Case-insensitive matching on process names
- Thread-safe access to whitelisted_session list
"""

import logging
import threading
import time
from typing import Callable, Optional

import psutil

from core.config_manager import load_config, get_launcher_for_game

logger = logging.getLogger("mindfun.game_detector")


class GameDetector:
    """
    Continuously monitors running processes for games in the configured list.

    When a game is found that isn't whitelisted, calls the on_game_detected callback
    with (game_exe, game_pid, launcher_exe, launcher_pid).
    """

    def __init__(self, on_game_detected: Callable[[str, int, Optional[str], Optional[int]], None]):
        """
        Args:
            on_game_detected: Callback function called when a new game is detected.
                Signature: (game_exe: str, game_pid: int, launcher_exe: str|None, launcher_pid: int|None)
        """
        self._on_game_detected = on_game_detected
        self._whitelisted_session: set[str] = set()
        self._active_pids: set[int] = set()  # PIDs currently being handled (prevent re-trigger)
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._paused = False

    def start(self):
        """Start the game detector polling loop in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("GameDetector already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, name="GameDetector", daemon=True)
        self._thread.start()
        logger.info("GameDetector started")

    def stop(self):
        """Stop the polling loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("GameDetector stopped")

    def pause(self):
        """Temporarily pause detection (e.g., 'Pause today' feature)."""
        self._paused = True
        logger.info("GameDetector paused")

    def resume(self):
        """Resume detection after pause."""
        self._paused = False
        logger.info("GameDetector resumed")

    def is_paused(self) -> bool:
        """Check if the detector is currently paused."""
        return self._paused

    def whitelist_game(self, game_exe: str):
        """
        Add a game to the whitelist for this session.
        Once whitelisted, the game will not trigger detection again until reset.
        """
        with self._lock:
            self._whitelisted_session.add(game_exe.lower())
            logger.info("Whitelisted '%s' for this session", game_exe)

    def remove_active_pid(self, pid: int):
        """Remove a PID from the active set (called when lockscreen closes)."""
        with self._lock:
            self._active_pids.discard(pid)

    def reset_whitelist(self):
        """Reset the whitelisted session list (called at 05:00 or on restart)."""
        with self._lock:
            self._whitelisted_session.clear()
            self._active_pids.clear()
            logger.info("Whitelist reset")

    def _poll_loop(self):
        """Main polling loop — runs every 3 seconds."""
        logger.info("Polling loop started")
        while self._running:
            try:
                if not self._paused:
                    self._scan_processes()
            except Exception as e:
                logger.error("Error in polling loop: %s", e, exc_info=True)

            # Sleep in small increments so we can stop quickly
            for _ in range(30):  # 30 × 0.1s = 3s
                if not self._running:
                    break
                time.sleep(0.1)

    def _scan_processes(self):
        """Scan all running processes and check against the game list."""
        config = load_config()
        game_list = {g.lower() for g in config.get("game_list", [])}

        if not game_list:
            return

        is_playing_whitelisted = False

        for proc in psutil.process_iter(["name", "pid"]):
            try:
                proc_name = proc.info.get("name", "")
                if not proc_name:
                    continue

                proc_name_lower = proc_name.lower()
                proc_pid = proc.info["pid"]

                # Check if this process matches a game in our list
                if proc_name_lower not in game_list:
                    continue

                with self._lock:
                    # If game is already whitelisted, we know user is playing it
                    if proc_name_lower in self._whitelisted_session:
                        is_playing_whitelisted = True
                        continue
                    if proc_pid in self._active_pids:
                        continue

                    # Mark as active to prevent re-triggering
                    self._active_pids.add(proc_pid)

                # Find the associated launcher
                launcher_exe = get_launcher_for_game(proc_name)
                launcher_pid = None
                if launcher_exe:
                    launcher_procs = self._find_process(launcher_exe)
                    if launcher_procs:
                        launcher_pid = launcher_procs[0].pid

                logger.info(
                    "Detected game: %s (PID %d), launcher: %s (PID %s)",
                    proc_name, proc_pid, launcher_exe, launcher_pid
                )

                # Trigger the callback (Soft Mode handler)
                self._on_game_detected(proc_name, proc_pid, launcher_exe, launcher_pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Update daily play time
        if is_playing_whitelisted:
            from core.report_logger import add_play_time
            add_play_time(3)  # Loop runs every 3 seconds

    def _find_process(self, name: str) -> list[psutil.Process]:
        """Find processes by name (case-insensitive)."""
        matches = []
        name_lower = name.lower()
        for proc in psutil.process_iter(["name", "pid"]):
            try:
                if proc.info["name"] and proc.info["name"].lower() == name_lower:
                    matches.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return matches
