#!/usr/bin/env python3
"""
DD1 Achievement Tracker
=======================
Reads your DunDefHeroes.dun save file and shows which of the 163
Dungeon Defenders achievements you have unlocked.

Usage:
    python achievement_tracker.py

Requirements:
    pip install -r requirements.txt

On first launch, click Browse and select your DunDefHeroes.dun save file.
The path is remembered in _ach_manual.json for later runs. All achievement
and map data is read from that .dun file; no Steam install scan is required.
"""
import sys, os, re, struct, json
from urllib.parse import quote as _url_quote

# ── Import parser (same directory) ───────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)

from dun_parser import (
    decompress_dun, BinaryReader,
    parse_options_info, parse_hero_info, parse_equipment,
    MAX_ACHIEVEMENTS,
    get_savefile_beaten_levels,
)

_MANUAL_JSON = os.path.join(_SCRIPT_DIR, "_ach_manual.json")
_INI_FILENAME = "UDKEngineSteamworks.ini"
_BUNDLED_ACH_INDEX_JSON = os.path.join(_SCRIPT_DIR, "steam_achievement_index.json")

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QLineEdit, QScrollArea, QFrame,
        QFileDialog, QSizePolicy, QProgressBar, QButtonGroup,
    )
    from PySide6.QtCore import Qt, QTimer, QUrl, QPoint
    from PySide6.QtGui import QFont, QColor, QDesktopServices
except ImportError:
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Dependency Missing",
            "PySide6 is not installed in the active Python environment.\n\n"
            "Please install it by running:\n"
            "pip install PySide6\n\n"
            f"Current Python: {sys.executable}"
        )
    except ImportError:
        pass
    print("\n[ERROR] PySide6 is not installed in this Python environment!", file=sys.stderr)
    print("Please run: pip install PySide6", file=sys.stderr)
    print(f"Current Python: {sys.executable}\n", file=sys.stderr)
    if sys.stdout is not None and sys.stderr is not None:
        try:
            if sys.stdin is not None and sys.stdin.isatty():
                input("Press Enter to exit...")
        except Exception:
            pass
    sys.exit(1)

from achievement_data import (
    ACHIEVEMENTS,
    ACH_STACKS_WITH,
    ACH_TIPS,
    CHIKU_SECTION_MEMBERS,
    CHIKU_SECTIONS,
    CHROMATIC_ALT_TAGS,
    CHROMATIC_MAPS,
    META_DEFS,
    META_SORT_GROUPS,
    RUTHLESS_CAMPAIGN_MAPS,
    RUTHLESS_CHALLENGE_MAPS,
    WIKI_OVERRIDES,
    _ACH_DEFAULT_INDEX,
    _ACH_META_COLOR,
    _CHIKU_SECTION_FOR,
    _CHIKU_SECTION_LOOKUP,
    _CHIKU_SORT_INDEX,
    _ETERNAL_REQS,
    _LEGENDARY_REQS,
    _META_GROUP_FOR,
    _META_GROUP_TITLE,
    _META_SECTION_KEYS,
    _NAME_TO_STEAMID,
    _NM_HC_BIT,
    _RUTHLESS_HC_BIT,
    _ULTIMATE_REQS,
)

_SORT_MODES = ("default", "chiku", "meta")
_SETTINGS_KEY = "_ui_settings"

# ── Manual state helpers ──────────────────────────────────────────────────────

def _load_manual(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _split_manual_state(raw: dict) -> tuple[dict, dict]:
    """Return (achievement_manual_checkboxes, ui_settings)."""
    settings = raw.get(_SETTINGS_KEY, {})
    if not isinstance(settings, dict):
        settings = {}
    manual = {k: v for k, v in raw.items() if k != _SETTINGS_KEY and isinstance(v, bool)}
    return manual, settings


def _save_manual(path: str, manual: dict, settings: dict | None = None) -> None:
    payload = dict(manual)
    if settings:
        payload[_SETTINGS_KEY] = settings
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Error saving manual state]: {e}", file=sys.stderr, flush=True)


def _ini_path_for_dun(dun_path: str) -> str:
    """Derive UDKEngineSteamworks.ini from a standard DunDefHeroes.dun path."""
    parts = os.path.normpath(dun_path).split(os.sep)
    try:
        idx = parts.index("Binaries")
    except ValueError:
        return ""
    game_root = os.sep.join(parts[:idx])
    return os.path.join(game_root, "UDKGame", "Config", _INI_FILENAME)


def _resolve_save_paths(
    dun_path: str | None,
    ini_path: str | None,
    ui_settings: dict,
) -> tuple[str, str]:
    """Use explicit paths, else last saved paths from _ach_manual.json, else none."""
    if dun_path and os.path.isfile(dun_path):
        ini = ini_path if ini_path and os.path.isfile(ini_path) else _ini_path_for_dun(dun_path)
        return dun_path, ini

    saved_dun = ui_settings.get("dun_path", "")
    if saved_dun and os.path.isfile(saved_dun):
        saved_ini = ui_settings.get("ini_path", "")
        ini = saved_ini if saved_ini and os.path.isfile(saved_ini) else _ini_path_for_dun(saved_dun)
        return saved_dun, ini

    return "", ""

# ── Wiki URL helpers ──────────────────────────────────────────────────────────
_WIKI_BASE = "https://dungeondefenders.wiki.gg/wiki/"


def _wiki_url(name: str) -> str:
    slug = WIKI_OVERRIDES.get(name)
    if slug is None:
        slug = _url_quote(name.replace(' ', '_'), safe=":!()")
    return _WIKI_BASE + slug

# ── Save-file parser ──────────────────────────────────────────────────────────

def load_ach_index(ini_path: str = "") -> list[str]:
    """Return Steam achievement IDs in save-byte order (game INI or bundled JSON)."""
    pattern = re.compile(r'AchievementMapping=\(SteamAchievementID="([^"]+)"', re.IGNORECASE)
    if ini_path and os.path.isfile(ini_path):
        result: list[str] = []
        with open(ini_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    result.append(m.group(1))
        if result:
            return result
    if os.path.isfile(_BUNDLED_ACH_INDEX_JSON):
        with open(_BUNDLED_ACH_INDEX_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list) and data:
            return [str(x) for x in data]
    raise FileNotFoundError(
        "Steam achievement index not found. Expected bundled "
        f"steam_achievement_index.json beside the script, or a valid {_INI_FILENAME}."
    )


def get_unlocked_steam_ids(dun_path: str, ini_path: str) -> set[str]:
    """Parse the .dun file and return the set of unlocked Steam achievement IDs."""
    data = decompress_dun(dun_path)
    r = BinaryReader(data)
    r.read_i32()   # version
    r.read_i32()   # size
    parse_options_info(r)
    hero_count = r.read_i32()
    for _ in range(hero_count):
        parse_hero_info(r)
        eq_count = r.read_i32()
        for _ in range(eq_count):
            parse_equipment(r)
    ach_bytes  = r.read(MAX_ACHIEVEMENTS)
    ach_values = list(struct.unpack_from(f'<{MAX_ACHIEVEMENTS}b', ach_bytes))
    ach_index  = load_ach_index(ini_path)
    unlocked = set()
    for idx, val in enumerate(ach_values):
        if val != 0 and idx < len(ach_index):
            unlocked.add(ach_index[idx])
    return unlocked

# ── UI typography & spacing (single source of truth — tune sizes here only) ───
UI_FONT: dict[str, int] = {
    "base":       17,
    "title":      24,
    "counter":    18,
    "status":     16,
    "search":     17,
    "button":     15,
    "toggle":     15,
    "section":    15,
    "blurb":      14,
    "ach_name":   17,
    "ach_desc":   15,
    "ach_detail": 14,
    "ach_badge":  15,
    "ach_dot":    20,
    "meta_title": 15,
    "meta_body":  15,
    "path":       15,
    "hint":       15,
}

UI_PAD: dict[str, int] = {
    "card_v":         8,
    "card_h":         12,
    "row_gap":        4,
    "toggle_x":       12,
    "toggle_y":       4,
    "button_x":       10,
    "button_y":       4,
    "toggle_slack_x": 10,
    "toggle_slack_y": 4,
}


def build_stylesheet(fonts: dict[str, int] | None = None) -> str:
    """Build the app stylesheet from UI_FONT so sizes stay in sync everywhere."""
    f = fonts or UI_FONT
    return f"""
QMainWindow, QWidget#root {{
    background: #1e1e1e;
    color: #d4d4d4;
}}
QWidget {{
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: {f['base']}px;
}}
QLabel#title {{
    font-size: {f['title']}px;
    font-weight: bold;
    color: #ffffff;
}}
QLabel#counter {{
    font-size: {f['counter']}px;
    color: #9cdcfe;
    font-weight: bold;
}}
QLabel#status_ok  {{ color: #4ec94e; font-size: {f['status']}px; }}
QLabel#status_err {{ color: #f48771; font-size: {f['status']}px; }}
QLabel#path_lbl   {{ color: #808080; font-size: {f['path']}px; }}
QLabel#hint_lbl   {{ color: #808080; font-size: {f['hint']}px; }}
QLineEdit#search {{
    background: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 6px 10px;
    color: #d4d4d4;
    font-size: {f['search']}px;
    min-height: {f['search'] + 8}px;
}}
QLineEdit#search:focus {{ border: 1px solid #007acc; }}
QPushButton {{
    background: #007acc;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: {UI_PAD['button_y']}px {UI_PAD['button_x']}px;
    font-size: {f['button']}px;
    font-weight: bold;
    min-height: {f['button'] + UI_PAD['button_y'] * 2 + 2}px;
}}
QPushButton:hover   {{ background: #1a8cdd; }}
QPushButton:pressed {{ background: #005fa3; }}
QPushButton#browse_btn {{ background: #3c3c3c; color: #d4d4d4; }}
QPushButton#browse_btn:hover {{ background: #4f4f4f; }}
QScrollArea {{ border: none; background: #1e1e1e; }}
QScrollBar:vertical {{ background: #2d2d2d; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: #555; border-radius: 4px; min-height: 20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QLabel#section_header {{
    font-size: {f['section']}px;
    font-weight: bold;
    color: #808080;
    letter-spacing: 1px;
    padding-top: 6px;
}}
QFrame#card, QFrame#card_done {{
    border-radius: 8px;
}}
QFrame#card      {{ background: #252526; border: 1px solid #2d2d2d; }}
QFrame#card_done {{ background: #1e2d1e; border: 1px solid #2d4a2d; }}
QFrame#meta_card, QFrame#meta_card_done {{
    border-radius: 8px;
    min-width: 145px;
}}
QFrame#meta_card      {{ background: #252526; border: 1px solid #2d2d2d; }}
QFrame#meta_card_done {{ background: #1e2d1e; border: 1px solid #2d4a2d; }}
QFrame#meta_card:hover, QFrame#meta_card_done:hover {{
    border: 2px solid #007acc;
    background: #2a2a2b;
}}
QPushButton#map_expand_btn_ruthless {{
    background: #c0392b;
    color: #ffffff;
    border: 3px solid #ff6b6b;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 16px;
    font-weight: bold;
    min-height: 52px;
    text-align: center;
}}
QPushButton#map_expand_btn_ruthless:hover {{
    background: #e74c3c;
    border-color: #ff8787;
}}
QPushButton#map_expand_btn_ruthless:pressed {{
    background: #922b21;
}}
QPushButton#map_expand_btn_chromatic {{
    background: #2471a3;
    color: #ffffff;
    border: 3px solid #5dade2;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 16px;
    font-weight: bold;
    min-height: 52px;
    text-align: center;
}}
QPushButton#map_expand_btn_chromatic:hover {{
    background: #3498db;
    border-color: #85c1e9;
}}
QPushButton#map_expand_btn_chromatic:pressed {{
    background: #1a5276;
}}
QFrame#map_row_done {{
    background: #1e2d1e;
    border: 1px solid #2d4a2d;
    border-radius: 6px;
}}
QFrame#map_row_missing {{
    background: #2d2525;
    border: 1px solid #5a3030;
    border-radius: 6px;
}}
QLabel#map_row_name_done {{
    color: #ffffff;
    font-weight: bold;
    font-size: {f['ach_desc']}px;
    background: transparent;
    border: none;
}}
QLabel#map_row_name_missing {{
    color: #f48771;
    font-weight: bold;
    font-size: {f['ach_desc']}px;
    background: transparent;
    border: none;
}}
QProgressBar {{ background: #3c3c3c; border: none; border-radius: 2px; }}
QProgressBar::chunk {{ background: #007acc; border-radius: 2px; }}
QPushButton#filter_btn, QPushButton#sort_btn {{
    background: #2d2d2d;
    color: #808080;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: {UI_PAD['toggle_y']}px {UI_PAD['toggle_x']}px;
    font-size: {f['toggle']}px;
    font-weight: normal;
    min-height: {f['toggle'] + UI_PAD['toggle_y'] * 2 + 2}px;
}}
QPushButton#sort_btn {{
    background: #252526;
}}
QPushButton#filter_btn:checked {{
    background: #007acc;
    color: #ffffff;
    border-color: #007acc;
}}
QPushButton#sort_btn:checked {{
    background: #264f78;
    color: #9cdcfe;
    border-color: #007acc;
}}
QPushButton#filter_btn:hover:!checked, QPushButton#sort_btn:hover:!checked {{
    background: #3c3c3c;
    color: #d4d4d4;
}}
QLabel#section_blurb {{
    font-size: {f['blurb']}px;
    color: #6a9955;
    font-style: italic;
    padding: 0 4px 6px 4px;
}}
QLabel#ach_name {{
    font-size: {f['ach_name']}px;
    font-weight: bold;
    color: #9d9d9d;
    background: transparent;
    border: none;
}}
QLabel#ach_name_done {{
    font-size: {f['ach_name']}px;
    font-weight: bold;
    color: #ffffff;
    background: transparent;
    border: none;
}}
QLabel#ach_desc {{
    font-size: {f['ach_desc']}px;
    color: #707070;
    background: transparent;
    border: none;
}}
QLabel#ach_tip {{
    font-size: {f['ach_detail']}px;
    color: #6eb3f7;
    background: transparent;
    border: none;
}}
QLabel#ach_stack {{
    font-size: {f['ach_detail']}px;
    color: #ce9178;
    background: transparent;
    border: none;
}}
QLabel#ach_meta_tag {{
    font-size: {f['ach_detail']}px;
    color: #999999;
    background: transparent;
    border: none;
}}
QLabel#ach_dot {{
    font-size: {f['ach_dot']}px;
    background: transparent;
    border: none;
}}
QLabel#ach_badge, QLabel#ach_badge_warn {{
    font-size: {f['ach_badge']}px;
    font-weight: bold;
    background: transparent;
    border: none;
}}
QLabel#ach_badge {{ color: #4ec94e; }}
QLabel#ach_badge_warn {{ color: #c5a028; }}
QLabel#meta_title {{
    font-size: {f['meta_title']}px;
    font-weight: bold;
    background: transparent;
    border: none;
}}
QLabel#meta_body {{
    font-size: {f['meta_body']}px;
    color: #808080;
    background: transparent;
    border: none;
}}
QLabel#meta_body_done {{
    font-size: {f['meta_body']}px;
    color: #4ec94e;
    font-weight: bold;
    background: transparent;
    border: none;
}}
"""


def _polish_widget(w) -> None:
    """Re-apply Qt styles so sizeHint() reflects the active stylesheet."""
    st = w.style()
    st.unpolish(w)
    st.polish(w)
    w.updateGeometry()


def _fit_toggle_button(btn) -> None:
    """Size toggle buttons from post-stylesheet sizeHint (no fixed width guessing)."""
    _polish_widget(btn)
    hint = btn.sizeHint()
    sx = UI_PAD["toggle_slack_x"]
    sy = UI_PAD["toggle_slack_y"]
    btn.setMinimumSize(hint.width() + sx, hint.height() + sy)
    btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)


def _fit_action_button(btn) -> None:
    """Size primary row buttons (Browse, Reload) after stylesheet is active."""
    _polish_widget(btn)
    hint = btn.sizeHint()
    btn.setMinimumSize(hint.width() + 4, hint.height() + 2)
    btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)


# Legacy name kept for any external imports
STYLESHEET = build_stylesheet()


def refresh_ui_fonts(widget: QWidget | None = None, *, delta: int = 0) -> str:
    """Rebuild stylesheet from UI_FONT. Pass delta to bump all sizes (e.g. +2)."""
    global STYLESHEET
    if delta:
        for key in UI_FONT:
            UI_FONT[key] += delta
    STYLESHEET = build_stylesheet()
    if widget is not None:
        widget.setStyleSheet(STYLESHEET)
        if hasattr(widget, "_apply_ui_metrics"):
            widget._apply_ui_metrics()
    return STYLESHEET

# ── Auto-unlock evaluation helpers ───────────────────────────────────────────

def _map_done_on_bit(beaten_levels: dict[str, int], tag: str, bit: int) -> bool:
    return (beaten_levels.get(tag, 0) & bit) != 0


def _chromatic_map_done(beaten_levels: dict[str, int], tag: str) -> bool:
    """True if map cleared on NM HC or Ruthless HC (primary tag or known Redux alias)."""
    tags = (tag,) + CHROMATIC_ALT_TAGS.get(tag, ())
    for t in tags:
        if _map_done_on_bit(beaten_levels, t, _NM_HC_BIT) or _map_done_on_bit(
            beaten_levels, t, _RUTHLESS_HC_BIT
        ):
            return True
    return False


def check_ruthless_defender(beaten_levels: dict[str, int]) -> bool:
    """Check if all 13 original campaign maps and 13 challenges are completed on Ruthless Hardcore."""
    if not beaten_levels:
        return False
    campaign_ok = all(
        _map_done_on_bit(beaten_levels, tag, _RUTHLESS_HC_BIT)
        for tag, _ in RUTHLESS_CAMPAIGN_MAPS
    )
    challenges_ok = all(
        _map_done_on_bit(beaten_levels, tag, _RUTHLESS_HC_BIT)
        for tag, _ in RUTHLESS_CHALLENGE_MAPS
    )
    return campaign_ok and challenges_ok


def check_chromatic_defender(beaten_levels: dict[str, int]) -> bool:
    """All Lost Quest + DDT challenge maps on NM HC after Ruthless Defender (wiki Chromatic Defender)."""
    if not beaten_levels:
        return False
    if not check_ruthless_defender(beaten_levels):
        return False
    return all(_chromatic_map_done(beaten_levels, tag) for tag, _ in CHROMATIC_MAPS)


def ruthless_map_status(beaten_levels: dict[str, int]) -> list[tuple[str, bool]]:
    """Return display name + done flag for every Ruthless HC campaign/challenge map."""
    maps: list[tuple[str, bool]] = []
    for tag, name in RUTHLESS_CAMPAIGN_MAPS:
        maps.append((f"{name} (Ruthless HC)", _map_done_on_bit(beaten_levels, tag, _RUTHLESS_HC_BIT)))
    for tag, name in RUTHLESS_CHALLENGE_MAPS:
        maps.append((f"{name} (Ruthless HC)", _map_done_on_bit(beaten_levels, tag, _RUTHLESS_HC_BIT)))
    return maps


def chromatic_map_status(beaten_levels: dict[str, int]) -> list[tuple[str, bool]]:
    """Return display name + done flag for Chromatic Defender maps (incl. Ruthless prereq)."""
    maps: list[tuple[str, bool]] = [
        ("Prerequisite: Ruthless Defender", check_ruthless_defender(beaten_levels)),
    ]
    for tag, name in CHROMATIC_MAPS:
        maps.append((f"{name} (NM HC)", _chromatic_map_done(beaten_levels, tag)))
    return maps


# ── Achievement row widget ────────────────────────────────────────────────────

class AchRow(QFrame):
    def __init__(self, name: str, desc: str, category: str, unlocked: bool,
                 dot_color: str = "#3c3c3c", wiki_url: str = "",
                 parent=None, auto_unlocked: bool = False,
                 tip: str = "", stacks: list[str] | None = None,
                 meta_tag: str = ""):
        super().__init__(parent)
        self.name = name
        self.desc = desc
        self.category = category
        self.unlocked = unlocked
        self.auto_unlocked = auto_unlocked
        self._dot_color = dot_color
        self._wiki_url = wiki_url
        self._tip = tip
        self._stacks = stacks or []
        self._meta_tag = meta_tag
        self._build()

    def _build(self):
        is_done = self.unlocked or self.auto_unlocked
        self.setObjectName("card_done" if is_done else "card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        if self._wiki_url:
            self.setCursor(Qt.PointingHandCursor)
            tooltip_parts = [self.desc]
            if self._tip:
                tooltip_parts.append(self._tip)
            if self._stacks:
                tooltip_parts.append("Stacks with: " + ", ".join(self._stacks))
            self.setToolTip("\n\n".join(tooltip_parts))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            UI_PAD["card_h"], UI_PAD["card_v"], UI_PAD["card_h"], UI_PAD["card_v"],
        )
        layout.setSpacing(12)

        accent = QFrame()
        accent.setFixedWidth(3)
        bar_color = "#4ec94e" if is_done else self._dot_color
        accent.setStyleSheet(
            f"background: {bar_color}; border-radius: 1px; "
            "border: none; min-width: 3px; max-width: 3px;"
        )
        layout.addWidget(accent)

        dot = QLabel("●")
        dot.setObjectName("ach_dot")
        dot.setFixedWidth(UI_FONT["ach_dot"] + 6)
        dot.setAlignment(Qt.AlignCenter)
        dot_color = "#4ec94e" if is_done else self._dot_color
        dot.setStyleSheet(f"color: {dot_color}; background: transparent; border: none;")
        layout.addWidget(dot)

        text_col = QVBoxLayout()
        text_col.setSpacing(UI_PAD["row_gap"])

        name_lbl = QLabel(self.name)
        name_lbl.setObjectName("ach_name_done" if is_done else "ach_name")
        name_lbl.setWordWrap(True)
        text_col.addWidget(name_lbl)

        desc_lbl = QLabel(self.desc)
        desc_lbl.setObjectName("ach_desc")
        desc_lbl.setWordWrap(True)
        text_col.addWidget(desc_lbl)

        if self._tip:
            tip_lbl = QLabel(self._tip)
            tip_lbl.setObjectName("ach_tip")
            tip_lbl.setWordWrap(True)
            text_col.addWidget(tip_lbl)

        if self._stacks:
            stack_lbl = QLabel("↳ Stacks with: " + ", ".join(self._stacks))
            stack_lbl.setObjectName("ach_stack")
            stack_lbl.setWordWrap(True)
            text_col.addWidget(stack_lbl)

        if self._meta_tag:
            meta_lbl = QLabel(self._meta_tag)
            meta_lbl.setObjectName("ach_meta_tag")
            meta_lbl.setWordWrap(True)
            text_col.addWidget(meta_lbl)

        layout.addLayout(text_col, stretch=1)

        if self.auto_unlocked and not self.unlocked:
            badge = QLabel("✓ Save Verified")
            badge.setObjectName("ach_badge")
        else:
            badge = QLabel("✓ Completed" if is_done else "Missing")
            badge.setObjectName("ach_badge" if is_done else "ach_badge_warn")
        badge.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        badge.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        layout.addWidget(badge)

    def mousePressEvent(self, event):
        if self._wiki_url and event.button() == Qt.LeftButton:
            QDesktopServices.openUrl(QUrl(self._wiki_url))
        super().mousePressEvent(event)


# ── Meta achievement progress card ────────────────────────────────────────────

class MetaCard(QFrame):
    def __init__(self, title: str, color: str, total: int, on_click=None, parent=None):
        super().__init__(parent)
        self._title = title
        self._color = color
        self._total = total
        self._missing: list[str] = []
        self._on_click = on_click
        self.setObjectName("meta_card")
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"Click to jump to {title} section")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, UI_PAD["card_v"], 10, UI_PAD["card_v"])
        layout.setSpacing(UI_PAD["row_gap"])

        self._title_lbl = QLabel(title)
        self._title_lbl.setObjectName("meta_title")
        self._title_lbl.setWordWrap(True)
        self._title_lbl.setStyleSheet(
            f"color: {color}; background: transparent; border: none;"
        )
        layout.addWidget(self._title_lbl)

        if total > 0:
            self._bar = QProgressBar()
            self._bar.setRange(0, total)
            self._bar.setValue(0)
            self._bar.setFixedHeight(5)
            self._bar.setTextVisible(False)
            self._bar.setStyleSheet(
                f"QProgressBar {{ background: #3c3c3c; border: none; border-radius: 2px; }}"
                f"QProgressBar::chunk {{ background: {color}; border-radius: 2px; }}"
            )
            layout.addWidget(self._bar)
        else:
            self._bar = None

        self._lbl = QLabel(f"0 / {total}" if total > 0 else "—")
        self._lbl.setObjectName("meta_body")
        layout.addWidget(self._lbl)

        jump_hint = QLabel("↳ Click to jump")
        jump_hint.setObjectName("meta_body")
        jump_hint.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: bold; "
            "background: transparent; border: none;"
        )
        layout.addWidget(jump_hint)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._on_click:
            self._on_click()
        super().mousePressEvent(event)

    def set_progress(self, done: int, is_complete: bool, missing: list[str] | None = None) -> None:
        self._missing = missing or []
        if self._missing:
            preview = ", ".join(self._missing[:8])
            if len(self._missing) > 8:
                preview += f", … (+{len(self._missing) - 8} more)"
            self.setToolTip(
                f"Click to jump to {self._title}\n\n"
                f"Missing ({len(self._missing)}):\n{preview}"
            )
        elif is_complete:
            self.setToolTip(f"Click to jump to {self._title} — complete")
        else:
            self.setToolTip(f"Click to jump to {self._title} — {done} / {self._total} complete")

        if is_complete:
            self.setObjectName("meta_card_done")
            self._lbl.setObjectName("meta_body_done")
            if self._bar:
                self._bar.setValue(self._total)
                self._lbl.setText(f"✓ {self._total} / {self._total}")
            else:
                self._lbl.setText("✓ Done")
        else:
            self.setObjectName("meta_card")
            self._lbl.setObjectName("meta_body")
            if self._bar:
                self._bar.setValue(done)
                missing_n = len(self._missing)
                suffix = f" · {missing_n} left" if missing_n else ""
                self._lbl.setText(f"{done} / {self._total}{suffix}")
            else:
                self._lbl.setText(f"{done} / {self._total}" if self._total else "—")
        _polish_widget(self._lbl)
        _polish_widget(self)


class MapTrackerPanel(QFrame):
    """Expandable per-map progress list for Ruthless / Chromatic Defender sections."""

    def __init__(
        self,
        section_key: str,
        beaten_levels: dict[str, int],
        filter_mode: str,
        parent=None,
    ):
        super().__init__(parent)
        self._section_key = section_key
        self._beaten_levels = beaten_levels
        self._filter_mode = filter_mode
        self._expanded = False
        self.setObjectName("card")
        self._build()

    def _all_maps(self) -> list[tuple[str, bool]]:
        if self._section_key == "ruthless":
            return ruthless_map_status(self._beaten_levels)
        return chromatic_map_status(self._beaten_levels)

    def _filtered_maps(self) -> list[tuple[str, bool]]:
        maps = self._all_maps()
        if self._filter_mode == "unlocked":
            return [(name, done) for name, done in maps if done]
        if self._filter_mode == "missing":
            return [(name, done) for name, done in maps if not done]
        return maps

    def _section_label(self) -> str:
        return "RUTHLESS HC" if self._section_key == "ruthless" else "CHROMATIC / NM HC"

    def _expand_btn_id(self) -> str:
        return (
            "map_expand_btn_ruthless"
            if self._section_key == "ruthless"
            else "map_expand_btn_chromatic"
        )

    def _update_expand_label(self) -> None:
        maps = self._filtered_maps()
        total_all = len(self._all_maps())
        done_all = sum(1 for _, done in self._all_maps() if done)
        missing_all = total_all - done_all
        label = self._section_label()

        if self._expanded:
            text = f"▲  COLLAPSE {label} MAP LIST  ▲"
        elif self._filter_mode == "missing":
            text = f"▼  EXPAND — SHOW {len(maps)} MISSING {label} MAPS  ▼"
        elif self._filter_mode == "unlocked":
            text = f"▼  EXPAND — SHOW {len(maps)} COMPLETED {label} MAPS  ▼"
        else:
            text = (
                f"▼  EXPAND — SHOW ALL {total_all} {label} MAPS "
                f"({done_all} done · {missing_all} missing)  ▼"
            )
        self._expand_btn.setText(text)

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 8)
        layout.setSpacing(6)

        self._expand_btn = QPushButton()
        self._expand_btn.setObjectName(self._expand_btn_id())
        self._expand_btn.clicked.connect(self._toggle)
        self._update_expand_label()
        layout.addWidget(self._expand_btn)

        self._content = QFrame()
        self._content.setVisible(False)
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)

        maps = self._filtered_maps()
        if maps:
            for name, done in maps:
                content_layout.addWidget(self._make_map_row(name, done))
        else:
            empty = QLabel("No maps match the current filter.")
            empty.setObjectName("section_blurb")
            empty.setWordWrap(True)
            content_layout.addWidget(empty)

        layout.addWidget(self._content)

    def _make_map_row(self, name: str, done: bool) -> QFrame:
        row = QFrame()
        row.setObjectName("map_row_done" if done else "map_row_missing")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setSpacing(10)

        dot = QLabel("●")
        dot.setFixedWidth(UI_FONT["ach_dot"] + 6)
        dot.setAlignment(Qt.AlignCenter)
        dot.setStyleSheet(
            f"color: {'#4ec94e' if done else '#f48771'}; background: transparent; border: none;"
        )
        row_layout.addWidget(dot)

        name_lbl = QLabel(name)
        name_lbl.setObjectName("map_row_name_done" if done else "map_row_name_missing")
        name_lbl.setWordWrap(True)
        row_layout.addWidget(name_lbl, stretch=1)

        badge = QLabel("✓ Done" if done else "Missing")
        badge.setObjectName("ach_badge" if done else "ach_badge_warn")
        badge.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_layout.addWidget(badge)
        return row

    def _toggle(self) -> None:
        self._expanded = not self._expanded
        self._content.setVisible(self._expanded)
        self._update_expand_label()


def _meta_group_key(name: str) -> str:
    return _META_GROUP_FOR.get(name, "other")


def _meta_group_title(key: str) -> str:
    return _META_GROUP_TITLE.get(key, "Other")


def _chiku_section_key(name: str) -> str:
    return _CHIKU_SECTION_FOR.get(name, "extras")


# ── Main window ───────────────────────────────────────────────────────────────

class AchievementTrackerWidget(QWidget):
    def __init__(self, parent=None, dun_path=None, ini_path=None):
        super().__init__(parent)

        _raw_manual = _load_manual(_MANUAL_JSON)
        self._manual_state, self._ui_settings = _split_manual_state(_raw_manual)
        self._sort_mode = self._ui_settings.get("sort_mode", "chiku")
        if self._sort_mode not in _SORT_MODES:
            self._sort_mode = "chiku"

        self._dun_path, self._ini_path = _resolve_save_paths(
            dun_path, ini_path, self._ui_settings,
        )
        self._unlocked:    set[str] = set()
        self._filter_mode  = "all"
        self._rows: list[AchRow]    = []
        self._beaten_levels: dict[str, int] = {}
        self._section_anchors: dict[str, QWidget] = {}
        self._pending_scroll_key: str | None = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 10, 16, 10)
        main_layout.setSpacing(5)

        top = QHBoxLayout()
        title = QLabel("DD1 Achievement Tracker")
        title.setObjectName("title")
        top.addWidget(title)
        top.addStretch()
        self._counter_lbl = QLabel("0 / 0")
        self._counter_lbl.setObjectName("counter")
        top.addWidget(self._counter_lbl)
        main_layout.addLayout(top)

        file_row = QHBoxLayout()
        self._path_lbl = QLabel("")
        self._path_lbl.setObjectName("path_lbl")
        self._path_lbl.setWordWrap(True)
        self._path_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        file_row.addWidget(self._path_lbl)
        self._browse_btn = QPushButton("Browse…")
        self._browse_btn.setObjectName("browse_btn")
        self._browse_btn.clicked.connect(self._browse)
        file_row.addWidget(self._browse_btn)
        self._reload_btn = QPushButton("Reload")
        self._reload_btn.clicked.connect(self._load)
        file_row.addWidget(self._reload_btn)
        main_layout.addLayout(file_row)

        self._status_lbl = QLabel("")
        self._status_lbl.setObjectName("status_ok")
        self._status_lbl.setWordWrap(True)
        main_layout.addWidget(self._status_lbl)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)
        self._meta_cards: list[MetaCard] = []
        _meta_totals = {
            "Legendary Defender": len(_LEGENDARY_REQS),
            "Ultimate Defender": len(_ULTIMATE_REQS),
            "Eternal Defender": len(_ETERNAL_REQS),
            "Ruthless Defender": len(RUTHLESS_CAMPAIGN_MAPS) + len(RUTHLESS_CHALLENGE_MAPS),
            "Chromatic Defender": len(CHROMATIC_MAPS),
        }
        for title_m, _sid, reqs, color in META_DEFS:
            total = _meta_totals.get(title_m, len(reqs))
            sec_key = _META_SECTION_KEYS[title_m]
            card = MetaCard(
                title_m, color, total,
                on_click=lambda k=sec_key: self._jump_to_meta_section(k),
            )
            meta_row.addWidget(card)
            self._meta_cards.append(card)
        main_layout.addLayout(meta_row)

        sort_row = QHBoxLayout()
        sort_row.setSpacing(6)
        sort_lbl = QLabel("Sort:")
        sort_lbl.setObjectName("hint_lbl")
        sort_row.addWidget(sort_lbl)
        self._sort_grp = QButtonGroup(self)
        self._sort_grp.setExclusive(True)
        for label, mode in [
            ("Chiku Guide", "chiku"),
            ("Meta Path", "meta"),
            ("Default", "default"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("sort_btn")
            btn.setCheckable(True)
            btn.setChecked(mode == self._sort_mode)
            btn.clicked.connect(lambda _checked, m=mode: self._set_sort_mode(m))
            self._sort_grp.addButton(btn)
            sort_row.addWidget(btn)
        sort_row.addStretch()
        main_layout.addLayout(sort_row)

        fs_row = QHBoxLayout()
        fs_row.setSpacing(6)
        filter_lbl = QLabel("Filter:")
        filter_lbl.setObjectName("hint_lbl")
        fs_row.addWidget(filter_lbl)
        self._filter_grp = QButtonGroup(self)
        self._filter_grp.setExclusive(True)
        for label, mode in [("All", "all"), ("Completed", "unlocked"), ("Missing", "missing")]:
            btn = QPushButton(label)
            btn.setObjectName("filter_btn")
            btn.setCheckable(True)
            btn.setChecked(mode == "all")
            btn.clicked.connect(lambda _checked, m=mode: self._set_filter(m))
            self._filter_grp.addButton(btn)
            fs_row.addWidget(btn)
        fs_row.addStretch()
        self._search = QLineEdit()
        self._search.setObjectName("search")
        self._search.setPlaceholderText("Search achievements…")
        self._search.textChanged.connect(self._rebuild_list)
        self._search.setMaximumWidth(280)
        self._search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        fs_row.addWidget(self._search)
        main_layout.addLayout(fs_row)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 4, 0)
        self._list_layout.setSpacing(4)
        self._list_layout.addStretch()
        self._scroll.setWidget(self._list_widget)
        main_layout.addWidget(self._scroll, stretch=1)

        self.setStyleSheet(STYLESHEET)
        self._apply_ui_metrics()
        self._update_path_label()
        QTimer.singleShot(0, self._load)

    def _update_path_label(self) -> None:
        self._path_lbl.setText(self._dun_path or "No save file selected")

    def _persist_save_paths(self) -> None:
        self._ui_settings["dun_path"] = self._dun_path
        self._ui_settings["ini_path"] = self._ini_path
        _save_manual(_MANUAL_JSON, self._manual_state, self._ui_settings)

    def _apply_ui_metrics(self) -> None:
        """Re-fit buttons after stylesheet is applied — safe to call after font changes."""
        for btn in self._sort_grp.buttons():
            _fit_toggle_button(btn)
        for btn in self._filter_grp.buttons():
            _fit_toggle_button(btn)
        _fit_action_button(self._browse_btn)
        _fit_action_button(self._reload_btn)


    def _jump_to_meta_section(self, section_key: str) -> None:
        if self._sort_mode != "meta":
            self._sort_mode = "meta"
            self._ui_settings["sort_mode"] = "meta"
            _save_manual(_MANUAL_JSON, self._manual_state, self._ui_settings)
            for btn in self._sort_grp.buttons():
                btn.setChecked(btn.text() == "Meta Path")
        self._pending_scroll_key = section_key
        self._rebuild_list()

    def _scroll_to_section(self, section_key: str) -> None:
        """Pin the section header to the top of the scroll viewport (not the section bottom)."""
        widget = self._section_anchors.get(section_key)
        content = self._scroll.widget()
        if not widget or content is None:
            return
        content.updateGeometry()
        top_margin = 8
        y = widget.mapTo(content, QPoint(0, 0)).y()
        bar = self._scroll.verticalScrollBar()
        bar.setValue(max(0, min(y - top_margin, bar.maximum())))

    def _load(self):
        if not self._dun_path or not os.path.isfile(self._dun_path):
            self._unlocked = set()
            self._beaten_levels = {}
            self._status_lbl.setObjectName("hint_lbl")
            self._status_lbl.setText(
                "No save loaded — click Browse… to select DunDefHeroes.dun"
            )
            self._status_lbl.setStyle(self._status_lbl.style())
            self._update_meta_cards()
            self._rebuild_list()
            return

        self._status_lbl.setObjectName("status_ok")
        try:
            self._unlocked = get_unlocked_steam_ids(self._dun_path, self._ini_path)
            self._beaten_levels = get_savefile_beaten_levels(self._dun_path)
            index_source = (
                "game INI"
                if self._ini_path and os.path.isfile(self._ini_path)
                else "bundled index"
            )
            self._status_lbl.setText(
                f"Loaded — {len(self._unlocked)} Steam achievements / "
                f"{len(self._beaten_levels)} level completions ({index_source})"
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._unlocked = set()
            self._beaten_levels = {}
            self._status_lbl.setObjectName("status_err")
            self._status_lbl.setText(f"Error: {e}")
        self._status_lbl.setStyle(self._status_lbl.style())
        self._update_meta_cards()
        self._rebuild_list()

    def _browse(self):
        start_dir = os.path.dirname(self._dun_path)
        if not start_dir or not os.path.isdir(start_dir):
            start_dir = os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, "Select DunDefHeroes.dun", start_dir,
            "DUN Files (*.dun);;All Files (*)"
        )
        if path:
            self._dun_path = path
            self._ini_path = _ini_path_for_dun(path)
            self._persist_save_paths()
            self._update_path_label()
            self._load()

    def _set_filter(self, mode: str) -> None:
        self._filter_mode = mode
        self._rebuild_list()

    def _set_sort_mode(self, mode: str) -> None:
        if mode not in _SORT_MODES:
            return
        self._sort_mode = mode
        self._ui_settings["sort_mode"] = mode
        _save_manual(_MANUAL_JSON, self._manual_state, self._ui_settings)
        self._rebuild_list()

    def _is_done(self, name: str, steam_id: str | None) -> tuple[bool, bool, bool]:
        """Return (is_done, unlocked_steam, auto_unlocked_manual)."""
        unlocked = (steam_id in self._unlocked) if steam_id else False
        auto_unlocked = False
        if steam_id is None:
            if name == "Ruthless Defender":
                auto_unlocked = check_ruthless_defender(self._beaten_levels)
            elif name == "Chromatic Defender":
                auto_unlocked = check_chromatic_defender(self._beaten_levels)
        is_done = unlocked or auto_unlocked
        return is_done, unlocked, auto_unlocked

    def _update_meta_cards(self) -> None:
        for card, (_title, self_sid, reqs, _color) in zip(self._meta_cards, META_DEFS):
            if _title == "Ruthless Defender":
                maps = ruthless_map_status(self._beaten_levels)
                missing = [name for name, done in maps if not done]
                done = sum(1 for _, d in maps if d)
                is_done = check_ruthless_defender(self._beaten_levels)
                if is_done:
                    missing = []
                card.set_progress(done, is_done, missing)
            elif _title == "Chromatic Defender":
                maps = chromatic_map_status(self._beaten_levels)
                missing = [name for name, done in maps if not done]
                done = sum(1 for name, d in maps if d and not name.startswith("Prerequisite"))
                is_done = check_chromatic_defender(self._beaten_levels)
                if is_done:
                    missing = []
                card.set_progress(done, is_done, missing)
            else:
                missing = []
                done = 0
                for req_name in reqs:
                    req_sid = _NAME_TO_STEAMID.get(req_name)
                    req_done, _, _ = self._is_done(req_name, req_sid)
                    if req_done:
                        done += 1
                    else:
                        missing.append(req_name)
                if self_sid:
                    is_done = self_sid in self._unlocked
                else:
                    is_done = done >= len(reqs)
                if is_done:
                    missing = []
                card.set_progress(done, is_done, missing)

    def _insert_section_block(self, header_key: str, title: str, blurb: str, suffix: str) -> None:
        hdr = QLabel(f"{title.upper()}{suffix}")
        hdr.setObjectName("section_header")
        hdr.setWordWrap(True)
        hdr.setContentsMargins(4, 10, 0, 0)
        if blurb:
            hdr.setToolTip(blurb)
        self._list_layout.insertWidget(self._list_layout.count() - 1, hdr)
        self._section_anchors[header_key] = hdr
        if blurb and self._sort_mode in ("chiku", "meta"):
            blurb_lbl = QLabel(blurb)
            blurb_lbl.setObjectName("section_blurb")
            blurb_lbl.setWordWrap(True)
            blurb_lbl.setContentsMargins(4, 0, 8, 4)
            self._list_layout.insertWidget(self._list_layout.count() - 1, blurb_lbl)
        if header_key in ("ruthless", "chromatic") and self._sort_mode in ("chiku", "meta"):
            panel = MapTrackerPanel(
                header_key,
                self._beaten_levels,
                self._filter_mode,
                parent=self._list_widget,
            )
            self._list_layout.insertWidget(self._list_layout.count() - 1, panel)

    def _section_key_for(self, name: str, category: str) -> str:
        if self._sort_mode == "default":
            return category
        if self._sort_mode == "chiku":
            return _chiku_section_key(name)
        return _meta_group_key(name)

    def _save_verified_section_suffix(self, section_key: str) -> str | None:
        """Ruthless/Chromatic headers show meta trophy progress plus map checklist progress."""
        if section_key == "ruthless":
            ach_done = 1 if check_ruthless_defender(self._beaten_levels) else 0
            maps_done = sum(1 for _, done in ruthless_map_status(self._beaten_levels) if done)
            map_total = len(RUTHLESS_CAMPAIGN_MAPS) + len(RUTHLESS_CHALLENGE_MAPS)
            return f" — {ach_done}/1 done ({maps_done}/{map_total} maps done)"
        if section_key == "chromatic":
            ach_done = 1 if check_chromatic_defender(self._beaten_levels) else 0
            maps_done = sum(
                1 for tag, _ in CHROMATIC_MAPS
                if _chromatic_map_done(self._beaten_levels, tag)
            )
            map_total = len(CHROMATIC_MAPS)
            return f" — {ach_done}/1 done ({maps_done}/{map_total} maps done)"
        return None

    def _header_for_section(self, section_key: str) -> tuple[str, str, str]:
        if self._sort_mode == "default":
            return (section_key.upper(), "", "")
        if self._sort_mode == "chiku":
            title, blurb = _CHIKU_SECTION_LOOKUP.get(section_key, ("Other", ""))
            save_suffix = self._save_verified_section_suffix(section_key)
            if save_suffix is not None:
                return (title, blurb, save_suffix)
            members = CHIKU_SECTION_MEMBERS.get(section_key, [])
            if members:
                done = sum(
                    1 for m in members
                    if self._is_done(m, _NAME_TO_STEAMID.get(m))[0]
                )
                suffix = f" — {done}/{len(members)} done"
            else:
                suffix = ""
            return (title, blurb, suffix)
        title = _meta_group_title(section_key)
        blurb = {
            "legendary": "Base game — 56 Steam achievements for Legendary Defender.",
            "ultimate": "Eternia Shards DLC — required after Legendary for Ultimate Defender.",
            "eternal": "CDT Lost Quests on Nightmare — after Ultimate Defender.",
            "ruthless": "Original campaign + challenges on Ruthless HC (save file verified).",
            "chromatic": "DDT endgame — after Ruthless Defender (save file verified).",
            "other": "Seasonal/DLC extras not required for core meta path.",
        }.get(section_key, "")
        save_suffix = self._save_verified_section_suffix(section_key)
        if save_suffix is not None:
            return (title, blurb, save_suffix)
        group_members = next((g[2] for g in META_SORT_GROUPS if g[0] == section_key), set())
        if group_members:
            done = sum(
                1 for m in group_members
                if self._is_done(m, _NAME_TO_STEAMID.get(m))[0]
            )
            suffix = f" — {done}/{len(group_members)} done"
        elif section_key == "other":
            other_names = [
                row[0] for row in ACHIEVEMENTS
                if _meta_group_key(row[0]) == "other"
            ]
            done = sum(
                1 for m in other_names
                if self._is_done(m, _NAME_TO_STEAMID.get(m))[0]
            )
            suffix = f" — {done}/{len(other_names)} done"
        else:
            suffix = ""
        return (title, blurb, suffix)

    def _add_entry_row(
        self,
        name: str,
        desc: str,
        cat: str,
        unlocked: bool,
        auto_unlocked: bool,
    ) -> None:
        tip = ACH_TIPS.get(name, "")
        stacks = ACH_STACKS_WITH.get(name, [])
        if self._filter_mode == "missing":
            stacks = [
                s for s in stacks
                if not self._is_done(s, _NAME_TO_STEAMID.get(s))[0]
            ]
        meta_tag = ""
        if self._sort_mode != "meta":
            gkey = _meta_group_key(name)
            if gkey != "other":
                meta_tag = f"Meta: {_meta_group_title(gkey)}"

        row = AchRow(
            name, desc, cat, unlocked,
            dot_color=_ACH_META_COLOR.get(name, "#3c3c3c"),
            wiki_url=_wiki_url(name),
            auto_unlocked=auto_unlocked,
            tip=tip,
            stacks=stacks,
            meta_tag=meta_tag,
        )
        self._list_layout.insertWidget(self._list_layout.count() - 1, row)
        self._rows.append(row)

    def _rebuild_list(self) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._rows = []
        self._section_anchors = {}
        query = self._search.text().lower().strip()

        entries: list[tuple] = []
        for name, desc, cat, steam_id in ACHIEVEMENTS:
            is_done, unlocked, auto_unlocked = self._is_done(name, steam_id)
            if self._filter_mode == "unlocked" and not is_done:
                continue
            if self._filter_mode == "missing" and is_done:
                continue
            if query and (
                query not in name.lower()
                and query not in desc.lower()
                and query not in cat.lower()
                and query not in ACH_TIPS.get(name, "").lower()
            ):
                continue
            entries.append((name, desc, cat, steam_id, is_done, unlocked, auto_unlocked))

        def _row_sort_key(entry):
            name = entry[0]
            if self._sort_mode == "chiku":
                sec = _chiku_section_key(name)
                sec_order = next(
                    (i for i, (k, _, _) in enumerate(CHIKU_SECTIONS) if k == sec),
                    len(CHIKU_SECTIONS),
                )
                return (sec_order, _CHIKU_SORT_INDEX.get(name, 10_000), name)
            if self._sort_mode == "meta":
                group_order = [g[0] for g in META_SORT_GROUPS]
                gkey = _meta_group_key(name)
                gidx = group_order.index(gkey) if gkey in group_order else len(group_order)
                return (gidx, _CHIKU_SORT_INDEX.get(name, 10_000), name)
            return (_ACH_DEFAULT_INDEX.get(name, 10_000),)

        entries.sort(key=_row_sort_key)

        scroll_target = self._pending_scroll_key

        if self._sort_mode in ("chiku", "meta"):
            grouped: dict[str, list[tuple]] = {}
            for entry in entries:
                grouped.setdefault(self._section_key_for(entry[0], entry[2]), []).append(entry)
            for force_key in ("ruthless", "chromatic"):
                grouped.setdefault(force_key, [])
            if scroll_target:
                grouped.setdefault(scroll_target, [])

            if self._sort_mode == "chiku":
                section_order = [k for k, _, _ in CHIKU_SECTIONS]
            else:
                section_order = [g[0] for g in META_SORT_GROUPS]

            for section_key in section_order:
                section_entries = grouped.get(section_key, [])
                if (
                    not section_entries
                    and section_key not in ("ruthless", "chromatic")
                    and section_key != scroll_target
                ):
                    continue
                h_title, h_blurb, h_suffix = self._header_for_section(section_key)
                self._insert_section_block(section_key, h_title, h_blurb, h_suffix)
                for name, desc, cat, _steam_id, _is_done, unlocked, auto_unlocked in section_entries:
                    self._add_entry_row(name, desc, cat, unlocked, auto_unlocked)
        else:
            current_section = None
            for name, desc, cat, steam_id, is_done, unlocked, auto_unlocked in entries:
                section_key = cat
                if section_key != current_section:
                    current_section = section_key
                    self._insert_section_block(section_key, cat.upper(), "", "")
                self._add_entry_row(name, desc, cat, unlocked, auto_unlocked)

        steam_total = sum(1 for *_, sid in ACHIEVEMENTS if sid)
        total_done = sum(1 for r in ACHIEVEMENTS if self._is_done(r[0], r[3])[0])
        missing_steam = steam_total - len(self._unlocked)
        self._counter_lbl.setText(
            f"{total_done} / {len(ACHIEVEMENTS)} total"
            f"  ·  {len(self._unlocked)} / {steam_total} Steam ({missing_steam} left)"
        )

        if self._pending_scroll_key:
            scroll_key = self._pending_scroll_key
            self._pending_scroll_key = None
            QTimer.singleShot(0, lambda k=scroll_key: self._scroll_to_section(k))
            QTimer.singleShot(80, lambda k=scroll_key: self._scroll_to_section(k))


class AchievementTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DD1 Achievement Tracker")
        self.resize(920, 760)
        self._widget = AchievementTrackerWidget(self)
        self.setCentralWidget(self._widget)


def check_single_instance(name: str):
    from PySide6.QtNetwork import QLocalSocket, QLocalServer
    from PySide6.QtWidgets import QMessageBox
    
    socket = QLocalSocket()
    socket.connectToServer(name)
    if socket.waitForConnected(500):
        socket.close()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Already Running")
        msg.setText("Another instance of the DD1 Achievement Tracker is already running.")
        msg.exec()
        sys.exit(0)
        
    QLocalServer.removeServer(name)
    server = QLocalServer()
    if not server.listen(name):
        sys.exit(1)
    return server


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    check_single_instance("dd1_achievement_tracker_lock")
    win = AchievementTracker()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
