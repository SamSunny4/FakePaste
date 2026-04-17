"""
FakePaste - Core Typing Engine
Simulates realistic human-like typing with natural variations,
typos, hesitations, and punctuation-aware pauses.
"""

import random
import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Callable

from pynput.keyboard import Controller, Key


class TypingState(Enum):
    IDLE = "idle"
    COUNTDOWN = "countdown"
    TYPING = "typing"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"


@dataclass
class TypingStats:
    """Analytics for a typing session."""
    total_chars: int = 0
    chars_typed: int = 0
    typos_made: int = 0
    corrections_made: int = 0
    pauses_used: int = 0
    total_pause_time: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    actual_keystrokes: int = 0

    @property
    def elapsed_time(self) -> float:
        if self.start_time == 0:
            return 0
        end = self.end_time if self.end_time > 0 else time.time()
        return end - self.start_time

    @property
    def avg_wpm(self) -> float:
        elapsed = self.elapsed_time
        if elapsed == 0:
            return 0
        return (self.chars_typed / 5.0) / (elapsed / 60.0)

    @property
    def accuracy(self) -> float:
        if self.actual_keystrokes == 0:
            return 100.0
        return max(0, (1 - self.typos_made / max(1, self.actual_keystrokes)) * 100)


@dataclass
class TypingConfig:
    """Configuration for typing behavior."""
    base_wpm: int = 60
    speed_variation: float = 0.25          # ±25% random speed variation
    accuracy_level: float = 0.97           # 97% accuracy (3% typo chance)
    punctuation_pause_min: float = 0.15    # Min extra pause after punctuation
    punctuation_pause_max: float = 0.6     # Max extra pause after punctuation
    paragraph_pause_min: float = 0.8       # Min pause for paragraph breaks
    paragraph_pause_max: float = 2.0       # Max pause for paragraph breaks
    word_pause_min: float = 0.02           # Min extra pause between words
    word_pause_max: float = 0.12           # Max extra pause between words
    hesitation_chance: float = 0.03        # 3% random hesitation
    hesitation_min: float = 0.3            # Min hesitation duration
    hesitation_max: float = 1.2            # Max hesitation duration
    thinking_pause_chance: float = 0.02    # 2% "thinking" pause
    thinking_pause_min: float = 0.5
    thinking_pause_max: float = 2.5
    delay_multiplier: float = 1.0          # Global delay multiplier
    preserve_line_breaks: bool = True
    typo_enabled: bool = True
    typo_max_length: int = 2               # Max wrong chars typed before correcting (1–4)
    countdown_seconds: int = 5
    repeat_mode: bool = False

    @property
    def base_delay(self) -> float:
        """Base delay between keystrokes in seconds."""
        if self.base_wpm <= 0:
            return 0.2
        # WPM -> chars per minute (avg 5 chars/word) -> delay per char
        cpm = self.base_wpm * 5.0
        return 60.0 / cpm


# Keyboard layout for realistic typo generation (QWERTY adjacency)
ADJACENT_KEYS = {
    'a': 'sqwz', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfcx',
    'e': 'wsdfr', 'f': 'dertgcv', 'g': 'frtyhvb', 'h': 'gyujbn',
    'i': 'ujklo', 'j': 'huiknm', 'k': 'jiolm', 'l': 'kop',
    'm': 'njk', 'n': 'bhjm', 'o': 'iklp', 'p': 'ol',
    'q': 'wa', 'r': 'edft', 's': 'awedxz', 't': 'rfgy',
    'u': 'yhjik', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc',
    'y': 'tghu', 'z': 'asx',
    '1': '2q', '2': '13qw', '3': '24we', '4': '35er',
    '5': '46rt', '6': '57ty', '7': '68yu', '8': '79ui',
    '9': '80io', '0': '9op',
}


class FakePaste:
    """
    Core engine that simulates human-like typing into any focused application.
    Uses pynput for cross-application keystroke injection.
    """

    def __init__(self):
        self.keyboard = Controller()
        self.config = TypingConfig()
        self.stats = TypingStats()
        self.state = TypingState.IDLE
        self._thread: Optional[threading.Thread] = None
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self._pause_event.set()  # Not paused initially

        # Callbacks
        self.on_state_change: Optional[Callable[[TypingState], None]] = None
        self.on_progress: Optional[Callable[[int, int, float], None]] = None
        self.on_countdown: Optional[Callable[[int], None]] = None
        self.on_char_typed: Optional[Callable[[str, int, int], None]] = None
        self.on_stats_update: Optional[Callable[[TypingStats], None]] = None
        self.on_completed: Optional[Callable[[TypingStats], None]] = None

    def _set_state(self, state: TypingState):
        self.state = state
        if self.on_state_change:
            self.on_state_change(state)

    def start(self, text: str):
        """Start typing the given text."""
        if self.state in (TypingState.TYPING, TypingState.COUNTDOWN):
            return

        self._stop_event.clear()
        self._pause_event.set()
        self.stats = TypingStats(total_chars=len(text))

        self._thread = threading.Thread(target=self._typing_loop, args=(text,), daemon=True)
        self._thread.start()

    def pause(self):
        """Pause typing."""
        if self.state == TypingState.TYPING:
            self._pause_event.clear()
            self._set_state(TypingState.PAUSED)

    def resume(self):
        """Resume typing."""
        if self.state == TypingState.PAUSED:
            self._pause_event.set()
            self._set_state(TypingState.TYPING)

    def stop(self):
        """Stop typing completely."""
        self._stop_event.set()
        self._pause_event.set()  # Unblock if paused
        self._set_state(TypingState.STOPPED)

    def emergency_stop(self):
        """Immediate stop via hotkey."""
        self.stop()

    def _should_stop(self) -> bool:
        return self._stop_event.is_set()

    def _wait_interruptible(self, duration: float) -> bool:
        """
        Wait for a duration, but can be interrupted by stop.
        Returns True if interrupted (should stop).
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            if self._should_stop():
                return True
            # Check pause
            self._pause_event.wait(timeout=0.05)
            if self._should_stop():
                return True
            time.sleep(min(0.02, end_time - time.time()))
        return False

    def _typing_loop(self, text: str):
        """Main typing loop running in a separate thread."""
        # --- Countdown Phase ---
        self._set_state(TypingState.COUNTDOWN)
        countdown = self.config.countdown_seconds
        for i in range(countdown, 0, -1):
            if self._should_stop():
                return
            if self.on_countdown:
                self.on_countdown(i)
            if self._wait_interruptible(1.0):
                return
        if self.on_countdown:
            self.on_countdown(0)

        # --- Typing Phase ---
        self._set_state(TypingState.TYPING)
        self.stats.start_time = time.time()

        while True:
            # Type through the text
            i = 0
            while i < len(text):
                if self._should_stop():
                    self.stats.end_time = time.time()
                    return

                # Handle pause
                self._pause_event.wait()
                if self._should_stop():
                    self.stats.end_time = time.time()
                    return

                char = text[i]

                # --- Pre-character delays ---

                # Word boundary pause (space)
                if char == ' ':
                    delay = random.uniform(
                        self.config.word_pause_min,
                        self.config.word_pause_max
                    ) * self.config.delay_multiplier
                    if self._wait_interruptible(delay):
                        self.stats.end_time = time.time()
                        return

                # Paragraph / line break pause
                if char == '\n':
                    if self.config.preserve_line_breaks:
                        delay = random.uniform(
                            self.config.paragraph_pause_min,
                            self.config.paragraph_pause_max
                        ) * self.config.delay_multiplier
                        self.stats.pauses_used += 1
                        self.stats.total_pause_time += delay
                        if self._wait_interruptible(delay):
                            self.stats.end_time = time.time()
                            return

                # Random hesitation
                if random.random() < self.config.hesitation_chance:
                    delay = random.uniform(
                        self.config.hesitation_min,
                        self.config.hesitation_max
                    ) * self.config.delay_multiplier
                    self.stats.pauses_used += 1
                    self.stats.total_pause_time += delay
                    if self._wait_interruptible(delay):
                        self.stats.end_time = time.time()
                        return

                # Random "thinking" pause
                if random.random() < self.config.thinking_pause_chance:
                    delay = random.uniform(
                        self.config.thinking_pause_min,
                        self.config.thinking_pause_max
                    ) * self.config.delay_multiplier
                    self.stats.pauses_used += 1
                    self.stats.total_pause_time += delay
                    if self._wait_interruptible(delay):
                        self.stats.end_time = time.time()
                        return

                # --- Typo simulation ---
                if (self.config.typo_enabled and
                        char.lower() in ADJACENT_KEYS and
                        random.random() > self.config.accuracy_level):
                    # Run typo sequence: type N wrong chars → backspace × N → continue
                    if self._do_typo_sequence(char):
                        self.stats.end_time = time.time()
                        return

                # --- Type the actual character ---
                self._type_char(char)
                self.stats.chars_typed += 1
                self.stats.actual_keystrokes += 1
                i += 1

                # --- Post-character delay ---
                # Base delay with variation
                base = self.config.base_delay
                variation = base * self.config.speed_variation
                delay = random.gauss(base, variation)
                delay = max(0.01, delay) * self.config.delay_multiplier

                # Extra delay after punctuation
                if char in '.?!':
                    extra = random.uniform(
                        self.config.punctuation_pause_min * 2,
                        self.config.punctuation_pause_max * 2
                    ) * self.config.delay_multiplier
                    delay += extra
                    self.stats.pauses_used += 1
                    self.stats.total_pause_time += extra
                elif char in ',;:':
                    extra = random.uniform(
                        self.config.punctuation_pause_min,
                        self.config.punctuation_pause_max
                    ) * self.config.delay_multiplier
                    delay += extra

                # Emit progress
                if self.on_progress:
                    progress = self.stats.chars_typed / max(1, self.stats.total_chars)
                    self.on_progress(self.stats.chars_typed, self.stats.total_chars, progress)

                if self.on_char_typed:
                    self.on_char_typed(char, self.stats.chars_typed, self.stats.total_chars)

                if self.on_stats_update:
                    self.on_stats_update(self.stats)

                if self._wait_interruptible(delay):
                    self.stats.end_time = time.time()
                    return

            # Check repeat mode
            if not self.config.repeat_mode:
                break
            else:
                # Reset stats for next loop (but keep cumulative)
                self.stats.chars_typed = 0

        # --- Completed ---
        self.stats.end_time = time.time()
        self._set_state(TypingState.COMPLETED)
        if self.on_completed:
            self.on_completed(self.stats)

    def _do_typo_sequence(self, intended_char: str) -> bool:
        """
        Simulate a realistic typo sequence:
          1. Type 1–N adjacent wrong characters (at normal inter-key speed)
          2. Pause briefly as the typist "notices" the mistake
          3. Backspace through each wrong character
          4. Pause briefly before retyping
        Returns True if we should stop (stop event fired).
        """
        cfg = self.config

        # Decide burst length: usually 1, occasionally 2 or 3
        max_burst = max(1, min(cfg.typo_max_length, 4))
        # Weighted: 1 wrong char is most common
        weights = [0.60, 0.28, 0.10, 0.02][:max_burst]
        total = sum(weights)
        weights = [w / total for w in weights]
        burst = random.choices(range(1, max_burst + 1), weights=weights, k=1)[0]

        adjacent = ADJACENT_KEYS[intended_char.lower()]
        wrong_chars = []

        # --- Phase 1: Type wrong characters ---
        for _ in range(burst):
            wc = random.choice(adjacent)
            if intended_char.isupper():
                wc = wc.upper()
            self._type_char(wc)
            wrong_chars.append(wc)
            self.stats.typos_made += 1
            self.stats.actual_keystrokes += 1
            # Brief inter-key delay between burst chars
            inter_delay = random.uniform(0.04, 0.10) * cfg.delay_multiplier
            if self._wait_interruptible(inter_delay):
                return True

        # --- Phase 2: Notice the error ---
        # Longer notice pause if more chars were typed wrong
        notice_base = random.uniform(0.10, 0.35)
        notice_delay = (notice_base + burst * 0.05) * cfg.delay_multiplier
        if self._wait_interruptible(notice_delay):
            return True

        # --- Phase 3: Backspace each wrong character ---
        for _ in range(burst):
            self.keyboard.press(Key.backspace)
            self.keyboard.release(Key.backspace)
            self.stats.corrections_made += 1
            self.stats.actual_keystrokes += 1
            # Small delay between backspaces (feels more human)
            bs_delay = random.uniform(0.04, 0.09) * cfg.delay_multiplier
            if self._wait_interruptible(bs_delay):
                return True

        # --- Phase 4: Brief pause before retyping correctly ---
        retype_delay = random.uniform(0.04, 0.14) * cfg.delay_multiplier
        if self._wait_interruptible(retype_delay):
            return True

        return False  # Continue normally — caller will type the correct char

    def _type_char(self, char: str):
        """Type a single character using pynput."""
        if char == '\n':
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)
        elif char == '\t':
            self.keyboard.press(Key.tab)
            self.keyboard.release(Key.tab)
        else:
            try:
                self.keyboard.type(char)
            except Exception:
                # Fallback for special/unicode characters
                try:
                    self.keyboard.press(char)
                    self.keyboard.release(char)
                except Exception:
                    pass

    def estimate_completion_time(self, text: str) -> float:
        """Estimate total typing time in seconds."""
        if not text:
            return 0
        base_time = len(text) * self.config.base_delay * self.config.delay_multiplier
        # Add ~15% overhead for pauses, hesitations, etc.
        overhead = 1.15
        if self.config.typo_enabled:
            # Add time for typo correction cycles
            typo_rate = 1 - self.config.accuracy_level
            overhead += typo_rate * 0.5
        return base_time * overhead

    def get_predicted_wpm(self) -> float:
        """Get predicted effective WPM based on config."""
        base = self.config.base_wpm
        if self.config.typo_enabled:
            typo_penalty = (1 - self.config.accuracy_level) * 15
            base -= typo_penalty
        return max(1, base / self.config.delay_multiplier)
