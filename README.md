# FakePaste 🎹

**Realistic human-like typing simulator for Windows**

FakePaste simulates natural, human-like typing into any application. Paste your text, press Start, switch to any window, and watch it type as if a real person were at the keyboard — complete with realistic speed variations, hesitations, and even occasional typos with corrections.

---

## ✨ Features

### Core
- 📝 Large multiline text input
- ▶️ Start / Pause / Resume / Stop controls
- ⏱ Configurable countdown (1-30 seconds) before typing begins
- 📊 Real-time progress bar with percentage
- 🔢 Live characters typed / remaining counter
- ⌛ Predicted completion time (ETA)
- ⚡ Global ESC hotkey for emergency stop

### Human-like Simulation
- 🎚 Adjustable typing speed (10-200 WPM)
- 🎲 Random speed variation per keystroke
- ⏳ Thinking delays between words
- 📌 Longer pauses after punctuation (. , ? ! : ;)
- 🔤 Realistic typo mode — makes small mistakes, backspaces, retypes correctly
- 💭 Random hesitation moments
- ¶ Paragraph break pauses

### Controls & Customization
- 🏷 Speed presets: Slow / Normal / Fast / Blazing / Custom
- 🎯 Accuracy slider (85%–100%)
- ⏩ Global delay multiplier
- 🔁 Repeat/loop mode
- 📐 Preserve or ignore line breaks
- 💾 Save/load custom presets

### Analytics
- 📈 Average WPM
- 🎯 Effective accuracy
- 🔢 Total keystrokes, typos, corrections
- ⏱ Session duration and pause time

### UI/UX
- 🌙 Premium dark mode interface
- 📋 Settings auto-saved on close
- ⚠️ Pre-start reminder to place cursor
- 🖥 Runs on Windows 10/11

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (for running from source)
- Windows 10 or 11

### Install from Source

```bash
# Clone / download the project
cd FakePaste

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Run the Standalone EXE

Just download `FakePaste.exe` from the releases and double-click to run. No installation required (portable mode).

Or use the installer (`FakePaste_Setup.exe`) for an installed experience with a desktop shortcut.

---

## 📖 Usage

1. **Open FakePaste**
2. **Paste your text** in the large text box
3. **Adjust settings** — pick a speed preset or customize WPM, accuracy, delays
4. **Click "▶ Start Typing"**
5. **A confirmation dialog appears** — click OK
6. **Countdown begins** — quickly switch to your target application and place your cursor
7. **Watch it type!** — the text types character by character with human-like behavior
8. **Press ESC** at any time for emergency stop

### Speed Presets

| Preset | WPM | Description |
|--------|-----|-------------|
| Slow | ~25 | Hunt-and-peck style |
| Normal | ~55 | Average typist |
| Fast | ~90 | Experienced typist |
| Blazing | ~130 | Professional speed |
| Custom | — | Your own settings |

---

## 🔧 Build from Source

### Build Standalone EXE

```bash
pip install pyinstaller
python build.py
```

The executable will be created at `dist/FakePaste.exe`.

### Build Installer

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Build the EXE first (see above)
3. Open `installer.iss` in Inno Setup Compiler
4. Click Build → Compile
5. Installer will be created in `installer_output/`

---

## 📁 Project Structure

```
FakePaste/
├── main.py              # Application entry point
├── core/
│   ├── typer.py         # Typing simulation engine
│   └── presets.py       # Speed preset definitions
├── ui/
│   ├── main_window.py   # Main window and all UI
│   └── styles.py        # Dark mode stylesheet
├── utils/
│   ├── settings.py      # Settings persistence
│   └── hotkeys.py       # Global hotkey manager
├── build.py             # PyInstaller build script
├── installer.iss        # Inno Setup installer script
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## ⚠️ Important Notes

- **ESC Key**: While FakePaste is typing, the ESC key globally stops all typing immediately.
- **Target App**: Make sure to click on the target application and place your cursor **during the countdown**.
- **Admin Rights**: No admin rights are required for normal text typing. Some protected applications may block simulated input.
- **Unicode**: Supports Unicode characters and emojis (dependent on the target application's support).

---

## 🛠 Tech Stack

- **Python 3.10+**
- **PyQt6** — Modern Qt-based GUI framework
- **pynput** — Cross-platform keyboard simulation
- **PyInstaller** — Standalone executable packaging
- **Inno Setup** — Windows installer creation

---

## 📜 License

MIT License — free for personal and commercial use.
