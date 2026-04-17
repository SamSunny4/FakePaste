"""
FakePaste - Dark Mode Stylesheet
Premium dark theme with accent colors and smooth visual design.
"""

# Color palette
COLORS = {
    'bg_primary': '#0d1117',
    'bg_secondary': '#161b22',
    'bg_tertiary': '#1c2333',
    'bg_card': '#1a1f2e',
    'bg_input': '#0d1117',
    'bg_hover': '#252d3a',
    'bg_pressed': '#2d3648',

    'border': '#30363d',
    'border_focus': '#58a6ff',
    'border_subtle': '#21262d',

    'text_primary': '#e6edf3',
    'text_secondary': '#8b949e',
    'text_muted': '#6e7681',
    'text_link': '#58a6ff',

    'accent': '#58a6ff',
    'accent_hover': '#79b8ff',
    'accent_dark': '#1f6feb',

    'success': '#3fb950',
    'success_dark': '#238636',
    'warning': '#d29922',
    'warning_dark': '#9e6a03',
    'danger': '#f85149',
    'danger_dark': '#da3633',

    'purple': '#bc8cff',
    'purple_dark': '#8b5cf6',
    'cyan': '#39d2c0',
    'orange': '#f0883e',

    'progress_bg': '#21262d',
    'progress_fill': '#58a6ff',
    'progress_glow': 'rgba(88, 166, 255, 0.3)',

    'scrollbar_bg': '#161b22',
    'scrollbar_handle': '#30363d',
    'scrollbar_hover': '#484f58',
}

DARK_STYLESHEET = f"""
/* ══════════════════════════════════════════════════
   GLOBAL APPLICATION STYLES
   ══════════════════════════════════════════════════ */

QMainWindow {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
}}

QWidget {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}

/* ══════════════════════════════════════════════════
   SCROLLBAR
   ══════════════════════════════════════════════════ */

QScrollBar:vertical {{
    background: {COLORS['scrollbar_bg']};
    width: 10px;
    margin: 0;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['scrollbar_handle']};
    min-height: 30px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['scrollbar_hover']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: {COLORS['scrollbar_bg']};
    height: 10px;
    margin: 0;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background: {COLORS['scrollbar_handle']};
    min-width: 30px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS['scrollbar_hover']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ══════════════════════════════════════════════════
   TEXT INPUT (MAIN TEXT BOX)
   ══════════════════════════════════════════════════ */

QPlainTextEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 14px;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
    selection-background-color: {COLORS['accent_dark']};
    selection-color: #ffffff;
}}

QPlainTextEdit:focus {{
    border: 1px solid {COLORS['border_focus']};
}}

QPlainTextEdit[readOnly="true"] {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_secondary']};
}}

/* ══════════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════════ */

QPushButton {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
    min-height: 18px;
}}

QPushButton:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['border_focus']};
}}

QPushButton:pressed {{
    background-color: {COLORS['bg_pressed']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_muted']};
    border-color: {COLORS['border_subtle']};
}}

/* Primary action button */
QPushButton#btn_start {{
    background-color: {COLORS['success_dark']};
    border-color: {COLORS['success']};
    color: #ffffff;
    font-size: 15px;
    padding: 12px 32px;
}}

QPushButton#btn_start:hover {{
    background-color: {COLORS['success']};
}}

QPushButton#btn_start:disabled {{
    background-color: {COLORS['bg_secondary']};
    border-color: {COLORS['border_subtle']};
    color: {COLORS['text_muted']};
}}

/* Pause button */
QPushButton#btn_pause {{
    background-color: {COLORS['warning_dark']};
    border-color: {COLORS['warning']};
    color: #ffffff;
}}

QPushButton#btn_pause:hover {{
    background-color: {COLORS['warning']};
}}

/* Stop button */
QPushButton#btn_stop {{
    background-color: {COLORS['danger_dark']};
    border-color: {COLORS['danger']};
    color: #ffffff;
}}

QPushButton#btn_stop:hover {{
    background-color: {COLORS['danger']};
}}

/* ══════════════════════════════════════════════════
   LABELS
   ══════════════════════════════════════════════════ */

QLabel {{
    color: {COLORS['text_primary']};
    background: transparent;
    padding: 0;
}}

QLabel#title_label {{
    font-size: 22px;
    font-weight: 700;
    color: {COLORS['text_primary']};
    padding: 4px 0;
}}

QLabel#subtitle_label {{
    font-size: 13px;
    color: {COLORS['text_secondary']};
}}

QLabel#section_label {{
    font-size: 14px;
    font-weight: 600;
    color: {COLORS['accent']};
    padding: 2px 0;
}}

QLabel#stat_value {{
    font-size: 20px;
    font-weight: 700;
    color: {COLORS['text_primary']};
}}

QLabel#stat_label {{
    font-size: 11px;
    color: {COLORS['text_secondary']};
    text-transform: uppercase;
}}

QLabel#countdown_label {{
    font-size: 72px;
    font-weight: 800;
    color: {COLORS['accent']};
}}

QLabel#warning_label {{
    color: {COLORS['warning']};
    font-size: 12px;
    font-style: italic;
}}

/* ══════════════════════════════════════════════════
   PROGRESS BAR
   ══════════════════════════════════════════════════ */

QProgressBar {{
    background-color: {COLORS['progress_bg']};
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    font-size: 10px;
    color: {COLORS['text_primary']};
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['accent_dark']},
        stop:1 {COLORS['accent']});
    border-radius: 6px;
}}

/* ══════════════════════════════════════════════════
   SLIDERS
   ══════════════════════════════════════════════════ */

QSlider::groove:horizontal {{
    background: {COLORS['progress_bg']};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {COLORS['accent']};
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
    border: 2px solid {COLORS['bg_primary']};
}}

QSlider::handle:horizontal:hover {{
    background: {COLORS['accent_hover']};
    width: 20px;
    height: 20px;
    margin: -7px 0;
    border-radius: 10px;
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['accent_dark']},
        stop:1 {COLORS['accent']});
    border-radius: 3px;
}}

/* ══════════════════════════════════════════════════
   COMBO BOX
   ══════════════════════════════════════════════════ */

QComboBox {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    min-width: 100px;
    font-size: 13px;
}}

QComboBox:hover {{
    border-color: {COLORS['border_focus']};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    selection-background-color: {COLORS['accent_dark']};
    selection-color: #ffffff;
    padding: 4px;
}}

/* ══════════════════════════════════════════════════
   SPIN BOX
   ══════════════════════════════════════════════════ */

QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['border_focus']};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background: transparent;
    border: none;
    width: 16px;
}}

/* ══════════════════════════════════════════════════
   CHECK BOX
   ══════════════════════════════════════════════════ */

QCheckBox {{
    spacing: 8px;
    color: {COLORS['text_primary']};
    font-size: 13px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid {COLORS['border']};
    background-color: {COLORS['bg_tertiary']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent_dark']};
    border-color: {COLORS['accent']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['accent']};
}}

/* ══════════════════════════════════════════════════
   GROUP BOX / CARDS
   ══════════════════════════════════════════════════ */

QGroupBox {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: 12px;
    margin-top: 16px;
    padding: 20px 16px 16px 16px;
    font-size: 13px;
    font-weight: 600;
    color: {COLORS['accent']};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    background-color: {COLORS['bg_card']};
    border-radius: 6px;
    color: {COLORS['accent']};
}}

/* ══════════════════════════════════════════════════
   TAB WIDGET
   ══════════════════════════════════════════════════ */

QTabWidget::pane {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: 0 0 12px 12px;
    padding: 8px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border_subtle']};
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    padding: 10px 20px;
    margin-right: 2px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['accent']};
    border-color: {COLORS['border']};
}}

QTabBar::tab:hover:!selected {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

/* ══════════════════════════════════════════════════
   TOOLTIP
   ══════════════════════════════════════════════════ */

QToolTip {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ══════════════════════════════════════════════════
   MENU BAR
   ══════════════════════════════════════════════════ */

QMenuBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border-bottom: 1px solid {COLORS['border_subtle']};
    padding: 2px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['bg_hover']};
    border-radius: 4px;
}}

QMenu {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {COLORS['accent_dark']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {COLORS['border_subtle']};
    margin: 4px 8px;
}}

/* ══════════════════════════════════════════════════
   STATUS BAR
   ══════════════════════════════════════════════════ */

QStatusBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border_subtle']};
    font-size: 12px;
    padding: 4px;
}}

/* ══════════════════════════════════════════════════
   LINE EDIT
   ══════════════════════════════════════════════════ */

QLineEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: {COLORS['accent_dark']};
}}

QLineEdit:focus {{
    border-color: {COLORS['border_focus']};
}}

/* ══════════════════════════════════════════════════
   FRAME CARD STYLE
   ══════════════════════════════════════════════════ */

QFrame#card {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: 12px;
    padding: 16px;
}}

QFrame#stat_card {{
    background-color: {COLORS['bg_tertiary']};
    border: 1px solid {COLORS['border_subtle']};
    border-radius: 10px;
    padding: 12px;
}}

/* ══════════════════════════════════════════════════
   DIALOG
   ══════════════════════════════════════════════════ */

QDialog {{
    background-color: {COLORS['bg_primary']};
}}

QMessageBox {{
    background-color: {COLORS['bg_primary']};
}}

QMessageBox QLabel {{
    color: {COLORS['text_primary']};
    font-size: 13px;
}}
"""
