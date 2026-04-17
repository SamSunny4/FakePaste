"""
FakePaste - Speed Presets
Pre-configured typing profiles for different use cases.
"""

from dataclasses import dataclass
from typing import Dict
from core.typer import TypingConfig


@dataclass
class SpeedPreset:
    """A named preset with description."""
    name: str
    description: str
    config: dict  # Partial config overrides


# Built-in presets
PRESETS: Dict[str, SpeedPreset] = {
    "slow": SpeedPreset(
        name="Slow",
        description="Hunt-and-peck style — careful, deliberate typing (~25 WPM)",
        config={
            "base_wpm": 25,
            "speed_variation": 0.35,
            "accuracy_level": 0.93,
            "punctuation_pause_min": 0.3,
            "punctuation_pause_max": 1.0,
            "paragraph_pause_min": 1.5,
            "paragraph_pause_max": 3.5,
            "word_pause_min": 0.05,
            "word_pause_max": 0.2,
            "hesitation_chance": 0.06,
            "thinking_pause_chance": 0.04,
            "delay_multiplier": 1.0,
        }
    ),
    "normal": SpeedPreset(
        name="Normal",
        description="Average typist — natural rhythm with occasional pauses (~55 WPM)",
        config={
            "base_wpm": 55,
            "speed_variation": 0.25,
            "accuracy_level": 0.97,
            "punctuation_pause_min": 0.15,
            "punctuation_pause_max": 0.6,
            "paragraph_pause_min": 0.8,
            "paragraph_pause_max": 2.0,
            "word_pause_min": 0.02,
            "word_pause_max": 0.12,
            "hesitation_chance": 0.03,
            "thinking_pause_chance": 0.02,
            "delay_multiplier": 1.0,
        }
    ),
    "fast": SpeedPreset(
        name="Fast",
        description="Experienced typist — quick and confident (~90 WPM)",
        config={
            "base_wpm": 90,
            "speed_variation": 0.15,
            "accuracy_level": 0.99,
            "punctuation_pause_min": 0.05,
            "punctuation_pause_max": 0.25,
            "paragraph_pause_min": 0.4,
            "paragraph_pause_max": 1.0,
            "word_pause_min": 0.01,
            "word_pause_max": 0.06,
            "hesitation_chance": 0.01,
            "thinking_pause_chance": 0.005,
            "delay_multiplier": 1.0,
        }
    ),
    "blazing": SpeedPreset(
        name="Blazing",
        description="Professional speed — minimal pauses (~130 WPM)",
        config={
            "base_wpm": 130,
            "speed_variation": 0.10,
            "accuracy_level": 0.995,
            "punctuation_pause_min": 0.02,
            "punctuation_pause_max": 0.1,
            "paragraph_pause_min": 0.2,
            "paragraph_pause_max": 0.5,
            "word_pause_min": 0.005,
            "word_pause_max": 0.03,
            "hesitation_chance": 0.005,
            "thinking_pause_chance": 0.002,
            "delay_multiplier": 1.0,
        }
    ),
}


def apply_preset(config: TypingConfig, preset_name: str) -> TypingConfig:
    """Apply a preset's values to a TypingConfig."""
    if preset_name not in PRESETS:
        return config
    preset = PRESETS[preset_name]
    for key, value in preset.config.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config


def get_preset_names() -> list:
    """Get list of available preset names."""
    return list(PRESETS.keys())


def get_preset_info(name: str) -> SpeedPreset:
    """Get preset information."""
    return PRESETS.get(name)
