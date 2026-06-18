"""
Mindfun — Night Guard

Monitors for games running during night hours (23:00–05:00) and applies
the appropriate response based on the current mode:
- Mode 1-3 (Silent Report): Log violation, track minutes, send toast on game exit
- Mode 4 (Hardcore Lockdown): Kill game immediately, send toast, log force_killed

Also handles the 05:00 daily reset of whitelisted_session.
"""

import logging
import threading
import time
from datetime import datetime, time as dt_time
from typing import Callable, Optional

import psutil

from core.config_manager import load_config
from core.i18n import t
from core.process_controller import is_process_running
from core import report_logger

logger = logging.getLogger("mindfun.night_guard")


def is_night_time() -> bool:
    """Check if the current time is within night hours (based on config)."""
    config = load_config()
    now = datetime.now().time()

    try:
        night_h, night_m = map(int, config.get("night_start", "23:00").split(":"))
        day_h, day_m = map(int, config.get("day_start", "05:00").split(":"))
    except (ValueError, AttributeError):
        night_h, night_m = 23, 0
        day_h, day_m = 5, 0

    night_start = dt_time(night_h, night_m)
    day_start = dt_time(day_h, day_m)

    # Night wraps around midnight: 23:00 → 05:00
    if night_start > day_start:
        return now >= night_start or now < day_start
    else:
        return night_start <= now < day_start


class NightGuard:
    """
    Monitors night-time gaming activity and enforces rules based on mode.
    """

    def __init__(
        self,
        on_whitelist_reset: Callable[[], None],
        on_toast: Callable[[str, str], None],
    ):
        """
        Args:
            on_whitelist_reset: Callback to reset the game detector's whitelist at 05:00.
            on_toast: Callback to show a toast notification. Signature: (title, message).
        """
        self._on_whitelist_reset = on_whitelist_reset
        self._on_toast = on_toast
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Track active night sessions: game_exe -> {pid, session_index, last_minute_update}
        self._active_sessions: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._last_reset_date: Optional[str] = None

    def start(self):
        """Start the night guard monitoring loop."""
        if self._thread and self._thread.is_alive():
            logger.warning("NightGuard already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, name="NightGuard", daemon=True)
        self._thread.start()
        logger.info("NightGuard started")

    def stop(self):
        """Stop the monitoring loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        logger.info("NightGuard stopped")

    def _monitor_loop(self):
        """Main monitoring loop — runs every 30 seconds."""
        logger.info("Night guard monitoring loop started")
        while self._running:
            try:
                self._check_night_rules()
                self._check_daily_reset()
            except Exception as e:
                logger.error("Error in night guard loop: %s", e, exc_info=True)

            # Sleep in small increments for responsive shutdown
            for _ in range(50):  # 50 × 0.1s = 5s
                if not self._running:
                    break
                time.sleep(0.1)



    def _check_night_rules(self):
        """Check for games running during night hours and enforce rules."""
        if not is_night_time():
            # Clean up any active sessions if we've left night time
            self._cleanup_ended_sessions()
            return

        config = load_config()
        mode = config.get("mode", 2)
        game_list = {g.lower() for g in config.get("game_list", [])}
        night_start = config.get("night_start", "23:00")

        if not game_list:
            return

        # Scan for running games
        found_games: dict[str, int] = {}  # exe_lower -> pid
        for proc in psutil.process_iter(["name", "pid"]):
            try:
                proc_name = proc.info.get("name", "")
                if proc_name and proc_name.lower() in game_list:
                    found_games[proc_name.lower()] = proc.info["pid"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Handle each found game
        for game_lower, pid in found_games.items():
            with self._lock:
                if game_lower in self._active_sessions:
                    # Already tracking — update violation minutes
                    session = self._active_sessions[game_lower]
                    now = time.time()
                    if now - session["last_minute_update"] >= 60:
                        report_logger.update_violation_minutes(session["session_index"])
                        session["last_minute_update"] = now
                else:
                    # New night violation detected
                    if mode >= 3:
                        # Hardcore: formerly killed, now we just notify and let detector overlay Lockscreen
                        logger.info("HARDCORE: Night violation %s (PID %d). Letting detector show Lockscreen.", game_lower, pid)
                        session_index = report_logger.start_session(game_lower, night_start)
                        report_logger.mark_notified(session_index)

                        now_str = datetime.now().strftime("%H:%M")
                        self._on_toast(
                            t("toast_title"),
                            t("toast_hardcore_kill", time=now_str),
                        )
                    else:
                        # Mode 1-2: Silent report + Toast remind
                        logger.info("Night violation: %s (PID %d), mode %d — silent tracking", game_lower, pid, mode)
                        session_index = report_logger.start_session(game_lower, night_start)
                        self._active_sessions[game_lower] = {
                            "pid": pid,
                            "session_index": session_index,
                            "last_minute_update": time.time(),
                        }
                        self._on_toast(
                            t("toast_title"),
                            t("toast_night_remind")
                        )

        # Check if any tracked games have exited
        self._cleanup_ended_sessions()

        # Update daily violation time (runs every 5s)
        if self._active_sessions:
            from core.report_logger import add_violation_time
            add_violation_time(5)

    def _cleanup_ended_sessions(self):
        """Finalize sessions for games that are no longer running."""
        with self._lock:
            ended = []
            for game_lower, session in self._active_sessions.items():
                if not is_process_running(session["pid"]):
                    ended.append(game_lower)

            for game_lower in ended:
                session = self._active_sessions.pop(game_lower)
                report_logger.finalize_session(session["session_index"])
                report_logger.mark_notified(session["session_index"])

                # Get the violation info for the toast
                sessions = report_logger.get_all_sessions()
                if 0 <= session["session_index"] < len(sessions):
                    session_data = sessions[session["session_index"]]
                    minutes = session_data.get("violation_minutes", 0)
                    game_name = session_data.get("game", game_lower)

                    self._on_toast(
                        t("toast_title"),
                        t("toast_night_report", game=game_name, minutes=minutes),
                    )
                    logger.info("Finalized night session for %s (%d violation minutes)", game_lower, minutes)

    def _check_daily_reset(self):
        """Reset whitelist at 05:00 every day and notify unnotified sessions."""
        config = load_config()
        try:
            day_h, day_m = map(int, config.get("day_start", "05:00").split(":"))
        except (ValueError, AttributeError):
            day_h, day_m = 5, 0

        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        # Only reset once per day, at or after the configured day_start time
        if self._last_reset_date == today:
            return

        if now.hour == day_h and now.minute >= day_m:
            logger.info("Daily reset triggered at %02d:%02d", day_h, day_m)
            self._last_reset_date = today

            # Reset whitelist
            self._on_whitelist_reset()

            # Reset daily tasks (checklist)
            from core.config_manager import reset_daily_tasks
            reset_daily_tasks()

            # Notify any unnotified sessions from last night
            unnotified = report_logger.get_unnotified_sessions()
            for idx, session_data in unnotified:
                minutes = session_data.get("violation_minutes", 0)
                game_name = session_data.get("game", "Unknown")
                self._on_toast(
                    t("toast_title"),
                    t("toast_night_report", game=game_name, minutes=minutes),
                )
                report_logger.mark_notified(idx)
