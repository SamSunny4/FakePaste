"""
FakePaste - Settings Manager
Save and load user preferences and custom presets.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

from core.typer import TypingConfig


def get_app_data_dir() -> Path:
    """Get the application data directory."""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    app_dir = Path(appdata) / 'FakePaste'
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_presets_dir() -> Path:
    """Get the custom presets directory."""
    presets_dir = get_app_data_dir() / 'presets'
    presets_dir.mkdir(parents=True, exist_ok=True)
    return presets_dir


def config_to_dict(config: TypingConfig) -> Dict[str, Any]:
    """Convert TypingConfig to a serializable dictionary."""
    return {
        'base_wpm': config.base_wpm,
        'speed_variation': config.speed_variation,
        'accuracy_level': config.accuracy_level,
        'punctuation_pause_min': config.punctuation_pause_min,
        'punctuation_pause_max': config.punctuation_pause_max,
        'paragraph_pause_min': config.paragraph_pause_min,
        'paragraph_pause_max': config.paragraph_pause_max,
        'word_pause_min': config.word_pause_min,
        'word_pause_max': config.word_pause_max,
        'hesitation_chance': config.hesitation_chance,
        'hesitation_min': config.hesitation_min,
        'hesitation_max': config.hesitation_max,
        'thinking_pause_chance': config.thinking_pause_chance,
        'thinking_pause_min': config.thinking_pause_min,
        'thinking_pause_max': config.thinking_pause_max,
        'delay_multiplier': config.delay_multiplier,
        'preserve_line_breaks': config.preserve_line_breaks,
        'typo_enabled': config.typo_enabled,
        'typo_max_length': config.typo_max_length,
        'countdown_seconds': config.countdown_seconds,
        'repeat_mode': config.repeat_mode,
    }


def dict_to_config(data: Dict[str, Any]) -> TypingConfig:
    """Create TypingConfig from a dictionary."""
    config = TypingConfig()
    for key, value in data.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config


def save_settings(config: TypingConfig, ui_settings: Optional[Dict] = None):
    """Save current settings to disk."""
    settings = {
        'typing_config': config_to_dict(config),
        'ui_settings': ui_settings or {},
    }
    settings_file = get_app_data_dir() / 'settings.json'
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


def load_settings() -> tuple:
    """Load settings from disk. Returns (TypingConfig, ui_settings_dict)."""
    settings_file = get_app_data_dir() / 'settings.json'
    if not settings_file.exists():
        return TypingConfig(), {}

    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        config = dict_to_config(settings.get('typing_config', {}))
        ui_settings = settings.get('ui_settings', {})
        return config, ui_settings
    except (json.JSONDecodeError, KeyError):
        return TypingConfig(), {}


def save_custom_preset(name: str, config: TypingConfig):
    """Save a custom preset."""
    preset_file = get_presets_dir() / f'{name}.json'
    data = config_to_dict(config)
    with open(preset_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_custom_preset(name: str) -> Optional[TypingConfig]:
    """Load a custom preset."""
    preset_file = get_presets_dir() / f'{name}.json'
    if not preset_file.exists():
        return None
    try:
        with open(preset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return dict_to_config(data)
    except (json.JSONDecodeError, KeyError):
        return None


def list_custom_presets() -> list:
    """List all custom preset names."""
    presets_dir = get_presets_dir()
    return [f.stem for f in presets_dir.glob('*.json')]


def delete_custom_preset(name: str):
    """Delete a custom preset."""
    preset_file = get_presets_dir() / f'{name}.json'
    if preset_file.exists():
        preset_file.unlink()
