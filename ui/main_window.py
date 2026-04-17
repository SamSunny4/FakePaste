"""
FakePaste - Main Window
Full-featured PyQt6 UI with text input, controls, progress tracking, and analytics.
"""

import time
import math
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPlainTextEdit, QPushButton, QLabel, QSlider, QComboBox,
    QProgressBar, QCheckBox, QSpinBox, QDoubleSpinBox,
    QGroupBox, QFrame, QTabWidget, QSplitter, QMessageBox,
    QStatusBar, QInputDialog, QSizePolicy, QApplication
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QObject, QSize, QPropertyAnimation,
    QEasingCurve, pyqtProperty, QParallelAnimationGroup
)
from PyQt6.QtGui import (
    QFont, QIcon, QColor, QPalette, QFontDatabase, QKeySequence,
    QShortcut, QPainter, QLinearGradient, QBrush
)

from core.typer import FakePaste, TypingState, TypingConfig, TypingStats
from core.presets import PRESETS, apply_preset, get_preset_names
from utils.settings import (
    save_settings, load_settings, save_custom_preset,
    load_custom_preset, list_custom_presets, delete_custom_preset,
    config_to_dict
)
from utils.hotkeys import HotkeyManager
from ui.styles import COLORS


# ─── Thread-safe signal bridge ──────────────────────────────────

class SignalBridge(QObject):
    """Bridge to emit Qt signals from background typing thread."""
    state_changed = pyqtSignal(str)
    progress_updated = pyqtSignal(int, int, float)
    countdown_tick = pyqtSignal(int)
    char_typed = pyqtSignal(str, int, int)
    stats_updated = pyqtSignal(object)
    typing_completed = pyqtSignal(object)


# ─── Animated Glowing Progress Bar ──────────────────────────────

class GlowProgressBar(QProgressBar):
    """Custom progress bar with glow effect."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setFixedHeight(10)


# ─── Stat Card Widget ───────────────────────────────────────────

class StatCard(QFrame):
    """A small card displaying a stat value and label."""

    def __init__(self, label: str, initial_value: str = "—", parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setFixedHeight(80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.value_label = QLabel(initial_value)
        self.value_label.setObjectName("stat_value")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel(label.upper())
        self.name_label.setObjectName("stat_label")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.value_label)
        layout.addWidget(self.name_label)

    def set_value(self, value: str):
        self.value_label.setText(value)


# ─── Main Window ────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """FakePaste main application window."""

    def __init__(self):
        super().__init__()

        # Core engine
        self.typer = FakePaste()
        self.signals = SignalBridge()
        self.hotkey_manager = HotkeyManager()

        # State
        self._current_text = ""
        self._countdown_active = False
        self._typing_start_time = 0

        # Load saved settings
        saved_config, saved_ui = load_settings()
        self.typer.config = saved_config

        # Setup
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._connect_typer_callbacks()
        self._setup_hotkeys()
        self._apply_saved_ui(saved_ui)
        self._update_eta()

        # Status bar timer
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_live_stats)
        self._status_timer.setInterval(500)

    # ─── Window Setup ───────────────────────────────────────────

    def _setup_window(self):
        self.setWindowTitle("FakePaste")
        self.setMinimumSize(980, 720)
        self.resize(1100, 800)

        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                (geo.width() - self.width()) // 2,
                (geo.height() - self.height()) // 2
            )

    # ─── UI Construction ────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)

        # ── Header ──
        header = self._create_header()
        main_layout.addLayout(header)

        # ── Main content: splitter with text area + controls ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Left panel: text input + progress
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel: controls tabs
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([600, 400])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter, 1)

        # ── Status bar ──
        self._setup_status_bar()

    def _create_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Title
        title_container = QVBoxLayout()
        title_container.setSpacing(2)

        title = QLabel("⌨  FakePaste")
        title.setObjectName("title_label")
        title_container.addWidget(title)

        subtitle = QLabel("Realistic human-like typing simulation")
        subtitle.setObjectName("subtitle_label")
        title_container.addWidget(subtitle)

        layout.addLayout(title_container)
        layout.addStretch()

        # Countdown display
        self.countdown_label = QLabel("")
        self.countdown_label.setObjectName("countdown_label")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFixedWidth(80)
        self.countdown_label.hide()
        layout.addWidget(self.countdown_label)

        # State indicator
        self.state_badge = QLabel("● IDLE")
        self.state_badge.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 12px;
                font-weight: 700;
                padding: 6px 14px;
                background-color: {COLORS['bg_tertiary']};
                border-radius: 12px;
                border: 1px solid {COLORS['border_subtle']};
            }}
        """)
        layout.addWidget(self.state_badge)

        return layout

    def _create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(12)

        # ── Text Input ──
        input_label = QLabel("📝  Text to Type")
        input_label.setObjectName("section_label")
        layout.addWidget(input_label)

        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText(
            "Paste or type your text here...\n\n"
            "The text will be typed character-by-character into\n"
            "whichever application has focus after the countdown."
        )
        self.text_input.setMinimumHeight(200)
        self.text_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_input, 1)

        # ── Character count ──
        char_row = QHBoxLayout()
        self.char_count_label = QLabel("0 characters · 0 words")
        self.char_count_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        char_row.addWidget(self.char_count_label)
        char_row.addStretch()

        self.eta_label = QLabel("ETA: —")
        self.eta_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        char_row.addWidget(self.eta_label)
        layout.addLayout(char_row)

        # ── Progress Section ──
        progress_frame = QFrame()
        progress_frame.setObjectName("card")
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(16, 14, 16, 14)
        progress_layout.setSpacing(10)

        # Progress bar
        prog_header = QHBoxLayout()
        prog_header.addWidget(QLabel("Progress"))
        self.progress_percent = QLabel("0%")
        self.progress_percent.setStyleSheet(f"color: {COLORS['accent']}; font-weight: 700;")
        prog_header.addStretch()
        prog_header.addWidget(self.progress_percent)
        progress_layout.addLayout(prog_header)

        self.progress_bar = GlowProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)

        self.stat_typed = StatCard("Typed", "0")
        self.stat_remaining = StatCard("Remaining", "0")
        self.stat_wpm = StatCard("WPM", "—")
        self.stat_accuracy = StatCard("Accuracy", "—")
        self.stat_elapsed = StatCard("Elapsed", "0:00")

        for card in [self.stat_typed, self.stat_remaining, self.stat_wpm,
                     self.stat_accuracy, self.stat_elapsed]:
            stats_row.addWidget(card)

        progress_layout.addLayout(stats_row)
        layout.addWidget(progress_frame)

        # ── Typo Mode Card (always-visible) ──
        typo_frame = QFrame()
        typo_frame.setObjectName("card")
        typo_frame.setStyleSheet(f"""
            QFrame#card {{
                background-color: {COLORS['bg_card']};
                border: 1px solid rgba(248, 81, 73, 0.35);
                border-radius: 12px;
                padding: 0;
            }}
        """)
        typo_layout = QVBoxLayout(typo_frame)
        typo_layout.setContentsMargins(14, 12, 14, 12)
        typo_layout.setSpacing(10)

        # Header row: toggle + label
        typo_header_row = QHBoxLayout()
        self.typo_check = QCheckBox()
        self.typo_check.setChecked(self.typer.config.typo_enabled)
        self.typo_check.stateChanged.connect(self._on_typo_toggled)

        typo_title = QLabel("🖊  Typo Mode")
        typo_title.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {COLORS['danger']};")

        typo_desc = QLabel("Types wrong characters, then backspaces and corrects")
        typo_desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")

        typo_header_row.addWidget(self.typo_check)
        typo_header_row.addWidget(typo_title)
        typo_header_row.addStretch()
        typo_layout.addLayout(typo_header_row)
        typo_layout.addWidget(typo_desc)

        # Controls row (accuracy + burst)
        typo_controls = QHBoxLayout()
        typo_controls.setSpacing(16)

        # Accuracy block
        acc_block = QVBoxLayout()
        acc_block.setSpacing(4)
        acc_top = QHBoxLayout()
        acc_top.addWidget(QLabel("Accuracy"))
        accuracy_pct = int(self.typer.config.accuracy_level * 100)
        self.accuracy_value = QLabel(f"{accuracy_pct}%")
        self.accuracy_value.setStyleSheet(f"color: {COLORS['success']}; font-weight: 700;")
        acc_top.addStretch()
        acc_top.addWidget(self.accuracy_value)
        acc_block.addLayout(acc_top)
        self.accuracy_slider = QSlider(Qt.Orientation.Horizontal)
        self.accuracy_slider.setRange(85, 100)
        self.accuracy_slider.setValue(accuracy_pct)
        self.accuracy_slider.setToolTip("Lower = more errors made")
        self.accuracy_slider.valueChanged.connect(self._on_accuracy_changed)
        acc_block.addWidget(self.accuracy_slider)
        typo_controls.addLayout(acc_block, 2)

        # Burst length block
        burst_block = QVBoxLayout()
        burst_block.setSpacing(4)
        burst_top = QHBoxLayout()
        burst_top.addWidget(QLabel("Max burst"))
        self.burst_value = QLabel(f"{self.typer.config.typo_max_length} chars")
        self.burst_value.setStyleSheet(f"color: {COLORS['danger']}; font-weight: 700;")
        burst_top.addStretch()
        burst_top.addWidget(self.burst_value)
        burst_block.addLayout(burst_top)
        self.burst_slider = QSlider(Qt.Orientation.Horizontal)
        self.burst_slider.setRange(1, 4)
        self.burst_slider.setValue(self.typer.config.typo_max_length)
        self.burst_slider.setToolTip("Max wrong characters typed in one typo burst (1 = single, 4 = up to 4 wrong chars)")
        self.burst_slider.valueChanged.connect(self._on_typo_burst_changed)
        burst_block.addWidget(self.burst_slider)
        typo_controls.addLayout(burst_block, 1)

        typo_layout.addLayout(typo_controls)

        # Example label
        burst_example = QLabel("1 = 'helo' → ⌫ → 'hello'   ·   3 = 'hxcvlo' → ⌫⌫⌫ → 'hello'")
        burst_example.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; font-style: italic;")
        typo_layout.addWidget(burst_example)

        # Enable/disable controls based on toggle
        self._typo_controls = [self.accuracy_slider, self.burst_slider, self.accuracy_value, self.burst_value]
        self._update_typo_controls_enabled()

        layout.addWidget(typo_frame)

        # ── Action Buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_start = QPushButton("▶  Start Typing")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.clicked.connect(self._on_start)
        self.btn_start.setToolTip("Start typing (you'll have a countdown to switch windows)")

        self.btn_pause = QPushButton("⏸  Pause")
        self.btn_pause.setObjectName("btn_pause")
        self.btn_pause.clicked.connect(self._on_pause_resume)
        self.btn_pause.setEnabled(False)

        self.btn_stop = QPushButton("⏹  Stop")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_stop.setEnabled(False)

        btn_row.addWidget(self.btn_start, 2)
        btn_row.addWidget(self.btn_pause, 1)
        btn_row.addWidget(self.btn_stop, 1)

        layout.addLayout(btn_row)

        # Warning
        self.warning_label = QLabel("⚠  Place your cursor in the target application before starting. Press ESC to emergency stop.")
        self.warning_label.setObjectName("warning_label")
        self.warning_label.setWordWrap(True)
        layout.addWidget(self.warning_label)

        return panel

    def _create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self._create_speed_tab(), "⚡ Speed")
        tabs.addTab(self._create_behavior_tab(), "🎭 Behavior")
        tabs.addTab(self._create_advanced_tab(), "⚙ Advanced")
        tabs.addTab(self._create_analytics_tab(), "📊 Analytics")

        layout.addWidget(tabs)
        return panel

    # ─── Speed Tab ──────────────────────────────────────────────

    def _create_speed_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        # Preset selector
        preset_group = QGroupBox("Speed Preset")
        preset_layout = QVBoxLayout(preset_group)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Custom", "custom")
        for key, preset in PRESETS.items():
            self.preset_combo.addItem(f"{preset.name}  —  {preset.description[:40]}...", key)

        # Add custom presets
        for name in list_custom_presets():
            self.preset_combo.addItem(f"💾 {name}", f"custom_{name}")

        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo)

        # Save preset button
        save_row = QHBoxLayout()
        btn_save_preset = QPushButton("💾 Save Current as Preset")
        btn_save_preset.clicked.connect(self._save_preset)
        save_row.addWidget(btn_save_preset)
        preset_layout.addLayout(save_row)

        layout.addWidget(preset_group)

        # WPM Slider
        wpm_group = QGroupBox("Typing Speed")
        wpm_layout = QVBoxLayout(wpm_group)

        wpm_header = QHBoxLayout()
        wpm_header.addWidget(QLabel("Words Per Minute"))
        self.wpm_value_label = QLabel(f"{self.typer.config.base_wpm} WPM")
        self.wpm_value_label.setStyleSheet(f"color: {COLORS['accent']}; font-weight: 700; font-size: 15px;")
        wpm_header.addStretch()
        wpm_header.addWidget(self.wpm_value_label)
        wpm_layout.addLayout(wpm_header)

        self.wpm_slider = QSlider(Qt.Orientation.Horizontal)
        self.wpm_slider.setRange(10, 200)
        self.wpm_slider.setValue(self.typer.config.base_wpm)
        self.wpm_slider.setTickInterval(10)
        self.wpm_slider.valueChanged.connect(self._on_wpm_changed)
        wpm_layout.addWidget(self.wpm_slider)

        # CPM display
        self.cpm_label = QLabel(f"≈ {self.typer.config.base_wpm * 5} CPM")
        self.cpm_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        wpm_layout.addWidget(self.cpm_label)

        layout.addWidget(wpm_group)

        # Speed variation
        var_group = QGroupBox("Speed Variation")
        var_layout = QVBoxLayout(var_group)

        var_header = QHBoxLayout()
        var_header.addWidget(QLabel("Randomness"))
        self.variation_value = QLabel(f"±{int(self.typer.config.speed_variation * 100)}%")
        self.variation_value.setStyleSheet(f"color: {COLORS['purple']}; font-weight: 600;")
        var_header.addStretch()
        var_header.addWidget(self.variation_value)
        var_layout.addLayout(var_header)

        self.variation_slider = QSlider(Qt.Orientation.Horizontal)
        self.variation_slider.setRange(0, 50)
        self.variation_slider.setValue(int(self.typer.config.speed_variation * 100))
        self.variation_slider.valueChanged.connect(self._on_variation_changed)
        var_layout.addWidget(self.variation_slider)

        layout.addWidget(var_group)

        layout.addStretch()
        return widget

    # ─── Behavior Tab ───────────────────────────────────────────

    def _create_behavior_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        # Accuracy / Typo settings (Behavior tab still has its own compact version)
        typo_group = QGroupBox("Accuracy & Typos")
        typo_layout = QVBoxLayout(typo_group)

        lnk_note = QLabel("ℹ  Typo Mode controls are also on the main panel (left side) for quick access.")
        lnk_note.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; font-style: italic;")
        lnk_note.setWordWrap(True)
        typo_layout.addWidget(lnk_note)

        acc_desc = QLabel("Accuracy: 100% = no typos · 85% = frequent errors with auto-correction")
        acc_desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        acc_desc.setWordWrap(True)
        typo_layout.addWidget(acc_desc)

        layout.addWidget(typo_group)

        # Pause behavior
        pause_group = QGroupBox("Pause Behavior")
        pause_layout = QVBoxLayout(pause_group)

        # Hesitation
        hes_header = QHBoxLayout()
        hes_header.addWidget(QLabel("Hesitation Frequency"))
        self.hesitation_value = QLabel(f"{int(self.typer.config.hesitation_chance * 100)}%")
        self.hesitation_value.setStyleSheet(f"color: {COLORS['cyan']}; font-weight: 600;")
        hes_header.addStretch()
        hes_header.addWidget(self.hesitation_value)
        pause_layout.addLayout(hes_header)

        self.hesitation_slider = QSlider(Qt.Orientation.Horizontal)
        self.hesitation_slider.setRange(0, 15)
        self.hesitation_slider.setValue(int(self.typer.config.hesitation_chance * 100))
        self.hesitation_slider.valueChanged.connect(self._on_hesitation_changed)
        pause_layout.addWidget(self.hesitation_slider)

        # Thinking pauses
        think_header = QHBoxLayout()
        think_header.addWidget(QLabel("Thinking Pauses"))
        self.thinking_value = QLabel(f"{int(self.typer.config.thinking_pause_chance * 100)}%")
        self.thinking_value.setStyleSheet(f"color: {COLORS['orange']}; font-weight: 600;")
        think_header.addStretch()
        think_header.addWidget(self.thinking_value)
        pause_layout.addLayout(think_header)

        self.thinking_slider = QSlider(Qt.Orientation.Horizontal)
        self.thinking_slider.setRange(0, 10)
        self.thinking_slider.setValue(int(self.typer.config.thinking_pause_chance * 100))
        self.thinking_slider.valueChanged.connect(self._on_thinking_changed)
        pause_layout.addWidget(self.thinking_slider)

        layout.addWidget(pause_group)

        # Line break handling
        lb_group = QGroupBox("Formatting")
        lb_layout = QVBoxLayout(lb_group)

        self.linebreak_check = QCheckBox("Preserve line breaks / paragraphs")
        self.linebreak_check.setChecked(self.typer.config.preserve_line_breaks)
        self.linebreak_check.stateChanged.connect(
            lambda s: setattr(self.typer.config, 'preserve_line_breaks', s == Qt.CheckState.Checked.value)
        )
        lb_layout.addWidget(self.linebreak_check)

        layout.addWidget(lb_group)

        layout.addStretch()
        return widget

    # ─── Advanced Tab ───────────────────────────────────────────

    def _create_advanced_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        # Countdown
        cd_group = QGroupBox("Countdown Timer")
        cd_layout = QHBoxLayout(cd_group)
        cd_layout.addWidget(QLabel("Seconds before typing starts:"))
        self.countdown_spin = QSpinBox()
        self.countdown_spin.setRange(1, 30)
        self.countdown_spin.setValue(self.typer.config.countdown_seconds)
        self.countdown_spin.valueChanged.connect(
            lambda v: setattr(self.typer.config, 'countdown_seconds', v)
        )
        cd_layout.addWidget(self.countdown_spin)
        layout.addWidget(cd_group)

        # Delay multiplier
        dm_group = QGroupBox("Delay Multiplier")
        dm_layout = QVBoxLayout(dm_group)

        dm_header = QHBoxLayout()
        dm_header.addWidget(QLabel("Global delay scale"))
        self.delay_mult_value = QLabel(f"{self.typer.config.delay_multiplier:.1f}×")
        self.delay_mult_value.setStyleSheet(f"color: {COLORS['warning']}; font-weight: 600;")
        dm_header.addStretch()
        dm_header.addWidget(self.delay_mult_value)
        dm_layout.addLayout(dm_header)

        self.delay_mult_slider = QSlider(Qt.Orientation.Horizontal)
        self.delay_mult_slider.setRange(1, 50)  # 0.1x to 5.0x
        self.delay_mult_slider.setValue(int(self.typer.config.delay_multiplier * 10))
        self.delay_mult_slider.valueChanged.connect(self._on_delay_mult_changed)
        dm_layout.addWidget(self.delay_mult_slider)

        dm_desc = QLabel("1.0× = normal · <1.0 = faster · >1.0 = slower")
        dm_desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        dm_layout.addWidget(dm_desc)

        layout.addWidget(dm_group)

        # Repeat mode
        repeat_group = QGroupBox("Repeat Mode")
        repeat_layout = QVBoxLayout(repeat_group)

        self.repeat_check = QCheckBox("Loop typing continuously")
        self.repeat_check.setChecked(self.typer.config.repeat_mode)
        self.repeat_check.stateChanged.connect(
            lambda s: setattr(self.typer.config, 'repeat_mode', s == Qt.CheckState.Checked.value)
        )
        repeat_layout.addWidget(self.repeat_check)

        repeat_desc = QLabel("Text will be typed again from the start when finished")
        repeat_desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        repeat_layout.addWidget(repeat_desc)

        layout.addWidget(repeat_group)

        # Settings management
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)

        btn_row = QHBoxLayout()
        btn_save = QPushButton("💾 Save Settings")
        btn_save.clicked.connect(self._save_all_settings)
        btn_row.addWidget(btn_save)

        btn_load = QPushButton("📂 Reset to Defaults")
        btn_load.clicked.connect(self._reset_defaults)
        btn_row.addWidget(btn_load)

        settings_layout.addLayout(btn_row)
        layout.addWidget(settings_group)

        layout.addStretch()
        return widget

    # ─── Analytics Tab ──────────────────────────────────────────

    def _create_analytics_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)

        # Session analytics
        analytics_group = QGroupBox("Session Analytics")
        analytics_layout = QVBoxLayout(analytics_group)

        self.analytics_labels = {}
        analytics_items = [
            ("avg_wpm", "Average WPM", "—"),
            ("total_keystrokes", "Total Keystrokes", "0"),
            ("typos_made", "Typos Made", "0"),
            ("corrections", "Corrections", "0"),
            ("pauses_count", "Pauses Used", "0"),
            ("total_pause_time", "Total Pause Time", "0.0s"),
            ("session_time", "Session Duration", "0:00"),
            ("effective_accuracy", "Effective Accuracy", "—"),
        ]

        for key, label_text, default in analytics_items:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            value = QLabel(default)
            value.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            analytics_layout.addLayout(row)
            self.analytics_labels[key] = value

        layout.addWidget(analytics_group)

        # Reset analytics
        btn_reset = QPushButton("🔄 Reset Analytics")
        btn_reset.clicked.connect(self._reset_analytics)
        layout.addWidget(btn_reset)

        layout.addStretch()
        return widget

    # ─── Status Bar ─────────────────────────────────────────────

    def _setup_status_bar(self):
        status = QStatusBar()
        self.setStatusBar(status)

        self.status_state = QLabel("Ready")
        self.status_hotkey = QLabel("ESC = Emergency Stop")
        self.status_hotkey.setStyleSheet(f"color: {COLORS['warning']};")

        status.addWidget(self.status_state, 1)
        status.addPermanentWidget(self.status_hotkey)

    # ─── Signal Connections ─────────────────────────────────────

    def _connect_signals(self):
        self.signals.state_changed.connect(self._handle_state_change)
        self.signals.progress_updated.connect(self._handle_progress)
        self.signals.countdown_tick.connect(self._handle_countdown)
        self.signals.char_typed.connect(self._handle_char_typed)
        self.signals.stats_updated.connect(self._handle_stats)
        self.signals.typing_completed.connect(self._handle_completed)

    def _connect_typer_callbacks(self):
        """Wire typer engine callbacks to emit Qt signals (thread-safe)."""
        self.typer.on_state_change = lambda s: self.signals.state_changed.emit(s.value)
        self.typer.on_progress = lambda typed, total, pct: self.signals.progress_updated.emit(typed, total, pct)
        self.typer.on_countdown = lambda n: self.signals.countdown_tick.emit(n)
        self.typer.on_char_typed = lambda c, typed, total: self.signals.char_typed.emit(c, typed, total)
        self.typer.on_stats_update = lambda stats: self.signals.stats_updated.emit(stats)
        self.typer.on_completed = lambda stats: self.signals.typing_completed.emit(stats)

    def _setup_hotkeys(self):
        self.hotkey_manager.register('esc', self._emergency_stop)
        self.hotkey_manager.start()

    # ─── Event Handlers ─────────────────────────────────────────

    def _on_text_changed(self):
        text = self.text_input.toPlainText()
        self._current_text = text
        chars = len(text)
        words = len(text.split()) if text.strip() else 0
        self.char_count_label.setText(f"{chars:,} characters · {words:,} words")
        self.stat_remaining.set_value(str(chars))
        self._update_eta()
        self.btn_start.setEnabled(chars > 0 and self.typer.state in (TypingState.IDLE, TypingState.STOPPED, TypingState.COMPLETED))

    def _on_start(self):
        text = self.text_input.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "No Text", "Please paste or type some text first.")
            return

        # Show confirmation
        countdown = self.typer.config.countdown_seconds
        reply = QMessageBox.information(
            self, "Ready to Type",
            f"After clicking OK, you have {countdown} seconds to:\n\n"
            f"1. Click on the target application\n"
            f"2. Place your cursor where you want to type\n\n"
            f"Text length: {len(text):,} characters\n"
            f"Estimated time: {self._format_time(self.typer.estimate_completion_time(text))}\n\n"
            f"Press ESC at any time to emergency stop.",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        if reply != QMessageBox.StandardButton.Ok:
            return

        self._set_buttons_typing()
        self._status_timer.start()
        self.typer.start(text)

    def _on_pause_resume(self):
        if self.typer.state == TypingState.TYPING:
            self.typer.pause()
            self.btn_pause.setText("▶  Resume")
        elif self.typer.state == TypingState.PAUSED:
            self.typer.resume()
            self.btn_pause.setText("⏸  Pause")

    def _on_stop(self):
        self.typer.stop()
        self._set_buttons_idle()
        self._status_timer.stop()

    def _emergency_stop(self):
        """Called from global hotkey (ESC)."""
        if self.typer.state in (TypingState.TYPING, TypingState.PAUSED, TypingState.COUNTDOWN):
            self.typer.emergency_stop()
            # Use signal to update UI from main thread
            self.signals.state_changed.emit(TypingState.STOPPED.value)

    # ─── Button State Management ────────────────────────────────

    def _set_buttons_typing(self):
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.text_input.setReadOnly(True)
        self.btn_pause.setText("⏸  Pause")

    def _set_buttons_idle(self):
        self.btn_start.setEnabled(bool(self._current_text.strip()))
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.text_input.setReadOnly(False)
        self.countdown_label.hide()

    # ─── Signal Handlers (UI Thread) ────────────────────────────

    def _handle_state_change(self, state_str: str):
        state_colors = {
            'idle': (COLORS['text_muted'], "IDLE"),
            'countdown': (COLORS['warning'], "COUNTDOWN"),
            'typing': (COLORS['success'], "TYPING"),
            'paused': (COLORS['warning'], "PAUSED"),
            'stopped': (COLORS['danger'], "STOPPED"),
            'completed': (COLORS['accent'], "COMPLETED"),
        }
        color, label = state_colors.get(state_str, (COLORS['text_muted'], state_str.upper()))
        self.state_badge.setText(f"● {label}")
        self.state_badge.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: 700;
                padding: 6px 14px;
                background-color: {COLORS['bg_tertiary']};
                border-radius: 12px;
                border: 1px solid {COLORS['border_subtle']};
            }}
        """)
        self.status_state.setText(f"State: {label}")

        if state_str in ('stopped', 'completed', 'idle'):
            self._set_buttons_idle()
            self._status_timer.stop()

    def _handle_countdown(self, seconds: int):
        if seconds > 0:
            self.countdown_label.setText(str(seconds))
            self.countdown_label.show()
        else:
            self.countdown_label.hide()

    def _handle_progress(self, typed: int, total: int, pct: float):
        self.progress_bar.setValue(int(pct * 1000))
        self.progress_percent.setText(f"{pct * 100:.1f}%")

    def _handle_char_typed(self, char: str, typed: int, total: int):
        self.stat_typed.set_value(f"{typed:,}")
        self.stat_remaining.set_value(f"{total - typed:,}")

    def _handle_stats(self, stats: TypingStats):
        # Update WPM
        if stats.elapsed_time > 2:
            wpm = stats.avg_wpm
            self.stat_wpm.set_value(f"{wpm:.0f}")

        # Accuracy
        self.stat_accuracy.set_value(f"{stats.accuracy:.1f}%")

    def _handle_completed(self, stats: TypingStats):
        self._set_buttons_idle()
        self._status_timer.stop()

        # Update final analytics
        self._update_analytics(stats)

        QMessageBox.information(
            self, "Typing Complete! ✅",
            f"Finished typing {stats.total_chars:,} characters!\n\n"
            f"Average WPM: {stats.avg_wpm:.1f}\n"
            f"Accuracy: {stats.accuracy:.1f}%\n"
            f"Typos made: {stats.typos_made}\n"
            f"Time: {self._format_time(stats.elapsed_time)}"
        )

    def _update_live_stats(self):
        """Update elapsed time display periodically."""
        if self.typer.state in (TypingState.TYPING, TypingState.PAUSED):
            elapsed = time.time() - self.typer.stats.start_time
            self.stat_elapsed.set_value(self._format_time(elapsed))

    # ─── Control Handlers ───────────────────────────────────────

    def _on_wpm_changed(self, value: int):
        self.typer.config.base_wpm = value
        self.wpm_value_label.setText(f"{value} WPM")
        self.cpm_label.setText(f"≈ {value * 5} CPM")
        self.preset_combo.setCurrentIndex(0)  # Switch to Custom
        self._update_eta()

    def _on_variation_changed(self, value: int):
        self.typer.config.speed_variation = value / 100.0
        self.variation_value.setText(f"±{value}%")

    def _on_accuracy_changed(self, value: int):
        self.typer.config.accuracy_level = value / 100.0
        self.accuracy_value.setText(f"{value}%")

    def _on_hesitation_changed(self, value: int):
        self.typer.config.hesitation_chance = value / 100.0
        self.hesitation_value.setText(f"{value}%")

    def _on_thinking_changed(self, value: int):
        self.typer.config.thinking_pause_chance = value / 100.0
        self.thinking_value.setText(f"{value}%")

    def _on_delay_mult_changed(self, value: int):
        mult = value / 10.0
        self.typer.config.delay_multiplier = mult
        self.delay_mult_value.setText(f"{mult:.1f}×")
        self._update_eta()

    def _on_typo_toggled(self, state):
        enabled = (state == Qt.CheckState.Checked.value)
        self.typer.config.typo_enabled = enabled
        self._update_typo_controls_enabled()

    def _on_typo_burst_changed(self, value: int):
        self.typer.config.typo_max_length = value
        labels = {1: "1 char", 2: "2 chars", 3: "3 chars", 4: "4 chars"}
        self.burst_value.setText(labels.get(value, f"{value} chars"))

    def _update_typo_controls_enabled(self):
        """Grey out typo sub-controls when typo mode is disabled."""
        enabled = self.typer.config.typo_enabled
        for w in self._typo_controls:
            w.setEnabled(enabled)
            w.setStyleSheet(
                w.styleSheet()   # keep existing colour when enabled
                if enabled
                else f"color: {COLORS['text_muted']}; font-weight: 400;"
            )

    def _on_preset_changed(self, index: int):
        if index <= 0:
            return  # Custom selected

        preset_key = self.preset_combo.itemData(index)
        if not preset_key:
            return

        if preset_key.startswith("custom_"):
            name = preset_key[7:]
            config = load_custom_preset(name)
            if config:
                self.typer.config = config
        else:
            apply_preset(self.typer.config, preset_key)

        # Update UI to reflect preset values
        self._sync_ui_from_config()

    def _sync_ui_from_config(self):
        """Sync all UI controls to match current config."""
        cfg = self.typer.config
        self.wpm_slider.blockSignals(True)
        self.wpm_slider.setValue(cfg.base_wpm)
        self.wpm_slider.blockSignals(False)
        self.wpm_value_label.setText(f"{cfg.base_wpm} WPM")
        self.cpm_label.setText(f"≈ {cfg.base_wpm * 5} CPM")

        self.variation_slider.blockSignals(True)
        self.variation_slider.setValue(int(cfg.speed_variation * 100))
        self.variation_slider.blockSignals(False)
        self.variation_value.setText(f"±{int(cfg.speed_variation * 100)}%")

        self.accuracy_slider.blockSignals(True)
        self.accuracy_slider.setValue(int(cfg.accuracy_level * 100))
        self.accuracy_slider.blockSignals(False)
        self.accuracy_value.setText(f"{int(cfg.accuracy_level * 100)}%")

        self.hesitation_slider.blockSignals(True)
        self.hesitation_slider.setValue(int(cfg.hesitation_chance * 100))
        self.hesitation_slider.blockSignals(False)
        self.hesitation_value.setText(f"{int(cfg.hesitation_chance * 100)}%")

        self.thinking_slider.blockSignals(True)
        self.thinking_slider.setValue(int(cfg.thinking_pause_chance * 100))
        self.thinking_slider.blockSignals(False)
        self.thinking_value.setText(f"{int(cfg.thinking_pause_chance * 100)}%")

        self.delay_mult_slider.blockSignals(True)
        self.delay_mult_slider.setValue(int(cfg.delay_multiplier * 10))
        self.delay_mult_slider.blockSignals(False)
        self.delay_mult_value.setText(f"{cfg.delay_multiplier:.1f}×")

        self.typo_check.setChecked(cfg.typo_enabled)
        self.burst_slider.blockSignals(True)
        self.burst_slider.setValue(cfg.typo_max_length)
        self.burst_slider.blockSignals(False)
        self.burst_value.setText(f"{cfg.typo_max_length} chars")
        self._update_typo_controls_enabled()
        self.linebreak_check.setChecked(cfg.preserve_line_breaks)
        self.countdown_spin.setValue(cfg.countdown_seconds)
        self.repeat_check.setChecked(cfg.repeat_mode)

        self._update_eta()

    # ─── Preset Management ──────────────────────────────────────

    def _save_preset(self):
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name.strip():
            save_custom_preset(name.strip(), self.typer.config)
            # Add to combo if not already there
            key = f"custom_{name.strip()}"
            found = False
            for i in range(self.preset_combo.count()):
                if self.preset_combo.itemData(i) == key:
                    found = True
                    break
            if not found:
                self.preset_combo.addItem(f"💾 {name.strip()}", key)
            QMessageBox.information(self, "Saved", f"Preset '{name.strip()}' saved successfully!")

    # ─── Settings ───────────────────────────────────────────────

    def _save_all_settings(self):
        save_settings(self.typer.config)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved.")

    def _reset_defaults(self):
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.typer.config = TypingConfig()
            self._sync_ui_from_config()
            self.preset_combo.setCurrentIndex(0)

    def _apply_saved_ui(self, ui_settings: dict):
        """Apply saved UI settings."""
        pass  # Placeholder for future window geometry, etc.

    # ─── Analytics ──────────────────────────────────────────────

    def _update_analytics(self, stats: TypingStats):
        self.analytics_labels['avg_wpm'].setText(f"{stats.avg_wpm:.1f}")
        self.analytics_labels['total_keystrokes'].setText(f"{stats.actual_keystrokes:,}")
        self.analytics_labels['typos_made'].setText(f"{stats.typos_made}")
        self.analytics_labels['corrections'].setText(f"{stats.corrections_made}")
        self.analytics_labels['pauses_count'].setText(f"{stats.pauses_used}")
        self.analytics_labels['total_pause_time'].setText(f"{stats.total_pause_time:.1f}s")
        self.analytics_labels['session_time'].setText(self._format_time(stats.elapsed_time))
        self.analytics_labels['effective_accuracy'].setText(f"{stats.accuracy:.1f}%")

    def _reset_analytics(self):
        for key in self.analytics_labels:
            if key in ('avg_wpm', 'effective_accuracy'):
                self.analytics_labels[key].setText("—")
            elif key == 'session_time':
                self.analytics_labels[key].setText("0:00")
            elif key == 'total_pause_time':
                self.analytics_labels[key].setText("0.0s")
            else:
                self.analytics_labels[key].setText("0")

    # ─── Utilities ──────────────────────────────────────────────

    def _update_eta(self):
        text = self._current_text
        if not text:
            self.eta_label.setText("ETA: —")
            return
        eta = self.typer.estimate_completion_time(text)
        self.eta_label.setText(f"ETA: ~{self._format_time(eta)}")

    @staticmethod
    def _format_time(seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            m = int(seconds // 60)
            s = int(seconds % 60)
            return f"{m}m {s:02d}s"
        else:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            return f"{h}h {m:02d}m"

    # ─── Cleanup ────────────────────────────────────────────────

    def closeEvent(self, event):
        """Clean up on window close."""
        self.typer.stop()
        self.hotkey_manager.stop()
        self._status_timer.stop()
        # Auto-save settings
        save_settings(self.typer.config)
        event.accept()
