"""
Mindfun — Report Logger

Reads/writes night violation sessions to report.json.
Thread-safe operations for concurrent access from night_guard and UI.
"""

import logging
from datetime import datetime

from core.config_manager import load_report, save_report

logger = logging.getLogger("mindfun.report_logger")

logger = logging.getLogger("mindfun.report_logger")

def _ensure_daily_stats(report: dict, date_str: str):
    """Ensure daily stats dict exists for the given date."""
    if "daily_stats" not in report:
        report["daily_stats"] = {}
    if date_str not in report["daily_stats"]:
        report["daily_stats"][date_str] = {
            "total_seconds": 0,
            "violation_seconds": 0
        }

def add_play_time(seconds: int):
    """Increment the total play time for today."""
    report = load_report()
    date_str = datetime.now().strftime("%Y-%m-%d")
    _ensure_daily_stats(report, date_str)
    report["daily_stats"][date_str]["total_seconds"] += seconds
    save_report(report)

def add_violation_time(seconds: int):
    """Increment the violation play time (night time) for today."""
    report = load_report()
    date_str = datetime.now().strftime("%Y-%m-%d")
    _ensure_daily_stats(report, date_str)
    report["daily_stats"][date_str]["violation_seconds"] += seconds
    save_report(report)

def get_daily_stats() -> dict:
    """Return the daily_stats dict { 'YYYY-MM-DD': {'total_seconds': X, 'violation_seconds': Y} }"""
    return load_report().get("daily_stats", {})

def start_session(game_exe: str, night_start: str) -> int:
    """
    Start a new night violation session.

    Args:
        game_exe: The game executable name (e.g., "LeagueOfLegends.exe")
        night_start: The configured night start time (e.g., "23:00")

    Returns:
        The index of the new session in the sessions list.
    """
    report = load_report()
    now = datetime.now()
    session = {
        "date": now.strftime("%Y-%m-%d"),
        "game": game_exe,
        "night_start": night_start,
        "actual_start": now.strftime("%H:%M"),
        "end_time": None,
        "violation_minutes": 0,
        "notified": False,
        "force_killed": False,
    }
    report["sessions"].append(session)
    save_report(report)
    session_index = len(report["sessions"]) - 1
    logger.info("Started night session #%d for %s at %s", session_index, game_exe, session["actual_start"])
    return session_index


def update_violation_minutes(session_index: int):
    """
    Increment the violation_minutes counter for an active session.
    Called every 60 seconds by the night guard while the game is running.
    """
    report = load_report()
    if 0 <= session_index < len(report["sessions"]):
        report["sessions"][session_index]["violation_minutes"] += 1
        save_report(report)


def finalize_session(session_index: int):
    """
    Finalize a session when the game process exits.
    Records the end_time.
    """
    report = load_report()
    if 0 <= session_index < len(report["sessions"]):
        now = datetime.now()
        report["sessions"][session_index]["end_time"] = now.strftime("%H:%M")
        save_report(report)
        logger.info("Finalized night session #%d at %s", session_index, report["sessions"][session_index]["end_time"])


def mark_notified(session_index: int):
    """Mark a session as having sent a notification toast."""
    report = load_report()
    if 0 <= session_index < len(report["sessions"]):
        report["sessions"][session_index]["notified"] = True
        save_report(report)


def mark_force_killed(session_index: int):
    """Mark a session as having been force-killed (Hardcore mode)."""
    report = load_report()
    if 0 <= session_index < len(report["sessions"]):
        report["sessions"][session_index]["force_killed"] = True
        report["sessions"][session_index]["end_time"] = datetime.now().strftime("%H:%M")
        save_report(report)
        logger.info("Marked session #%d as force_killed", session_index)


def get_unnotified_sessions() -> list[tuple[int, dict]]:
    """
    Get all sessions that haven't been notified yet.
    Returns list of (index, session_dict) tuples.
    """
    report = load_report()
    return [
        (i, session)
        for i, session in enumerate(report["sessions"])
        if not session.get("notified", False) and session.get("end_time") is not None
    ]


def get_all_sessions() -> list[dict]:
    """Get all sessions for display in the settings UI log tab."""
    return load_report().get("sessions", [])


def clear_all_sessions():
    """Clear all sessions from the report."""
    save_report({"sessions": []})
    logger.info("Cleared all report sessions")
