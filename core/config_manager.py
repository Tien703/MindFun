"""
Mindfun — Config Manager

Centralized configuration loading/saving with thread-safe file I/O.
All data files live in %APPDATA%/Mindfun/ for the current user.
"""

import json
import os
import shutil
import threading
from pathlib import Path

# Lock for thread-safe file operations
_file_lock = threading.Lock()
_system_language_synced = False

# Resolve paths
_APPDATA_DIR = Path(os.environ.get("APPDATA", "")) / "Mindfun"
_BUNDLE_DIR = Path(__file__).resolve().parent.parent / "data"


def get_data_dir() -> Path:
    """Get the user data directory (%APPDATA%/Mindfun/), creating it if needed."""
    try:
        _APPDATA_DIR.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass
    return _APPDATA_DIR


def get_data_path(filename: str) -> Path:
    """Get the full path to a data file in the user data directory."""
    return get_data_dir() / filename


def _ensure_defaults():
    """Copy default data files from bundle to %APPDATA%/Mindfun/ if they don't exist."""
    data_dir = get_data_dir()
    default_files = ["config.json", "questions.json", "report.json"]
    for fname in default_files:
        dest = data_dir / fname
        src = _BUNDLE_DIR / fname
        if not dest.exists() and src.exists():
            shutil.copy2(src, dest)


def _read_json(filepath: Path) -> dict:
    """Read a JSON file with thread safety."""
    with _file_lock:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


def _write_json(filepath: Path, data: dict):
    """Write a JSON file with thread safety and atomic write."""
    with _file_lock:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = filepath.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp_path.replace(filepath)


# ─── Config ──────────────────────────────────────────────────────────

def load_config() -> dict:
    """Load config.json from user data directory."""
    _ensure_defaults()
    config = _read_json(get_data_path("config.json"))
    # Ensure required fields with defaults
    config.setdefault("mode", 2)
    config.setdefault("day_start", "05:00")
    config.setdefault("night_start", "23:00")
    config.setdefault("language", "vi")
    config.setdefault("game_list", [])
    config.setdefault("anti_cheat", True)
    config.setdefault("dev_mode", False)
    config.setdefault("dark_mode", True)
    config.setdefault("onboarding_completed", False)
    
    config.setdefault("theme", {
        "primary_accent": "#f2b42c",
        "bg_dark": "#202020",
        "card_dark": "#2D2D2D",
        "bg_light": "#F3F3F3",
        "card_light": "#FFFFFF",
        "success_accent": "#b6f36d",
        "danger_accent": "#fe413c"
    })
    
    config.setdefault("sound", {
        "checklist_sound": "assets/sounds/checklist_sounds/check_1.wav",
        "notification_sound": "assets/sounds/notification_sounds/notif_1.wav",
        "play_checklist": True,
        "play_notification": True
    })
    
    # Check if we need to run daily reset on startup
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    last_reset = config.get("last_reset_date")
    
    # Try parsing day_start
    try:
        day_h, day_m = map(int, config.get("day_start", "05:00").split(":"))
    except Exception:
        day_h, day_m = 5, 0
        
    now = datetime.now()
    # If today is different from last_reset AND we are past the reset time
    if today != last_reset and (now.hour > day_h or (now.hour == day_h and now.minute >= day_m)):
        reset_daily_tasks()
        config["last_reset_date"] = today
        save_config(config)
        
    global _system_language_synced
    if not _system_language_synced:
        update_system_questions_language(config["language"])
        _system_language_synced = True
        
    return config

def save_config(config: dict):
    """Save config.json to user data directory."""
    _write_json(get_data_path("config.json"), config)


# ─── Questions ───────────────────────────────────────────────────────

import uuid

def load_questions() -> dict:
    """Load questions.json. Returns dict with 'task_groups' key containing per-language lists."""
    _ensure_defaults()
    data = _read_json(get_data_path("questions.json"))
    
    # Migration: from old "questions" list to new "task_groups"
    if "task_groups" not in data:
        data["task_groups"] = {"vi": [], "en": []}
        
        # Move old questions into a Philosophy group
        old_questions = data.get("questions", {})
        for lang, q_list in old_questions.items():
            if lang not in data["task_groups"]:
                data["task_groups"][lang] = []
            if q_list:
                data["task_groups"][lang].append({
                    "id": uuid.uuid4().hex,
                    "name": "🔵 Triết lý (Philosophy)" if lang == "vi" else "🔵 Philosophy",
                    "enabled": True,
                    "is_checklist": False,
                    "items": [{"id": uuid.uuid4().hex, "text": q, "done": False} for q in q_list]
                })
        

        save_questions(data)
    # NEW MIGRATION: Convert task_groups dict to list
    if isinstance(data.get("task_groups"), dict):
        merged_groups = []
        tg = data["task_groups"]
        # Convert any custom groups that might be in the dict
        for _, group_list in tg.items():
            for g in group_list:
                if not str(g.get("id", "")).startswith("default_"):
                    merged_groups.append(g)
        data["task_groups"] = merged_groups
        save_questions(data)
        
        # Now pull in the correct language defaults
        # We can't call load_config here to prevent circular dependency?
        # config is already loaded before load_questions in most cases, but let's be safe.
        update_system_questions_language("vi") # Will be corrected on first config load or language switch
        
    return data

def update_system_questions_language(lang: str):
    """Swap system default questions to match the newly selected language."""
    data = load_questions()
    groups = data.get("task_groups", [])
    
    # Check if already correct to avoid redundant writes
    current_defaults = [g for g in groups if str(g.get("id", "")).startswith("default_")]
    if current_defaults:
        if str(current_defaults[0].get("id", "")).startswith(f"default_{lang}_"):
            return
            
    # Keep only custom groups (those without 'default_' prefix)
    custom_groups = [g for g in groups if not str(g.get("id", "")).startswith("default_")]
    
    # Load default groups for the new language from bundle
    bundle_path = _BUNDLE_DIR / "questions.json"
    system_groups = []
    if bundle_path.exists():
        with open(bundle_path, "r", encoding="utf-8") as f:
            try:
                bundle_data = json.load(f)
                system_groups = bundle_data.get("task_groups", {}).get(lang, [])
            except Exception:
                pass
                
    # Place system groups at the top
    data["task_groups"] = system_groups + custom_groups
    save_questions(data)

def reset_daily_tasks():
    """Reset all 'done' flags to False across all checklist items."""
    data = load_questions()
    changed = False
    groups = data.get("task_groups", [])
    if isinstance(groups, dict):
        groups = groups.get("vi", []) + groups.get("en", [])
        
    for group in groups:
        if group.get("is_checklist", False):
            for item in group.get("items", []):
                if item.get("done", False):
                    item["done"] = False
                    changed = True
    if changed:
        save_questions(data)


def save_questions(data: dict):
    """Save questions.json."""
    _write_json(get_data_path("questions.json"), data)


# ─── Game Presets ────────────────────────────────────────────────────

def load_game_presets() -> dict:
    """Load game_presets.json directly from the app bundle (read-only)."""
    data = _read_json(_BUNDLE_DIR / "game_presets.json")
    data.setdefault("presets", [])
    return data

# We don't save game_presets.json to APPDATA anymore since it's read-only



# ─── Report ──────────────────────────────────────────────────────────

def load_report() -> dict:
    """Load report.json."""
    _ensure_defaults()
    data = _read_json(get_data_path("report.json"))
    data.setdefault("sessions", [])
    return data


def save_report(data: dict):
    """Save report.json."""
    _write_json(get_data_path("report.json"), data)


# ─── Launcher Lookup ─────────────────────────────────────────────────

def get_launcher_for_game(game_exe: str) -> str | None:
    """Look up the launcher executable for a given game executable."""
    presets = load_game_presets().get("presets", [])
    game_lower = game_exe.lower()
    for preset in presets:
        if preset.get("exe", "").lower() == game_lower:
            return preset.get("launcher")
    return None

def get_game_name(game_exe: str) -> str:
    """Look up the friendly name for a game executable. Fallback to exe name without extension."""
    game_lower = game_exe.lower()
    
    # Check custom games first
    custom_games = load_config().get("custom_games", [])
    for cg in custom_games:
        if cg.get("exe", "").lower() == game_lower:
            return cg.get("name", game_exe)
            
    # Check presets
    presets = load_game_presets().get("presets", [])
    for preset in presets:
        if preset.get("exe", "").lower() == game_lower:
            return preset.get("name", game_exe)
            
    # Fallback: remove .exe extension if present
    if game_lower.endswith(".exe"):
        return game_exe[:-4]
    return game_exe
