# DD1 Achievement Tracker

A desktop GUI tool for tracking all **163 Dungeon Defenders 1 achievements** — including 118 Steam-tracked achievements read directly from your save file, plus 45 non-Steam (CDT/DDT) achievements with manual checkboxes.

![Dark VS Code-style UI with achievement cards, meta progress bars, filter buttons, and search](./.github/preview.png)

---

## Features

- **Auto-detects your save file** from common Steam library paths on launch
- **Browse any `.dun` file** — works with your own save or anyone else's
- **Real-time search** and **All / Unlocked / Missing** filter
- **5 meta achievement progress cards** (Legendary → Ultimate → Eternal → Ruthless → Chromatic) with colored progress bars
- **Color-coded accent bars** show which meta path each achievement contributes to
- **Manual checkboxes** for CDT Manual and DDT Manual achievements (state saved to `_ach_manual.json`)
- **Clickable rows** open the achievement's wiki page

---

## Requirements

- Python 3.10 or newer
- PySide6

```
pip install PySide6
```

---

## Usage

```
python achievement_tracker.py
```

On first launch the app scans drives C–G for a Steam installation of Dungeon Defenders.  
If your Steam library is on a different drive, click **Browse…** and navigate to:

```
<SteamLibrary>\steamapps\common\Dungeon Defenders\Binaries\Win32\DunDefHeroes.dun
```

The achievement index is read from:

```
<SteamLibrary>\steamapps\common\Dungeon Defenders\UDKGame\Config\UDKEngineSteamworks.ini
```

Both files are included with every Steam installation of the game.

---

## Non-Steam Achievements

45 achievements added by the **Community Development Team (CDT)** and the **DD Together (DDT)** update are not stored in the `.dun` file.  
These appear with a checkbox — tick them yourself when you've earned them.  
Your checkbox state is saved automatically to `_ach_manual.json` next to the script.

### Meta achievements

| Achievement | How to earn |
|---|---|
| **Legendary Defender** | All 56 base-game Steam achievements |
| **Ultimate Defender** | Legendary Defender + all Eternia Shards DLC Steam achievements |
| **Eternal Defender** | Ultimate Defender + all CDT Lost Quests on Nightmare |
| **Ruthless Defender** | Original campaign + challenges on Ruthless Hardcore *(manual)* |
| **Chromatic Defender** | Ruthless Defender + all DDT maps on Nightmare Hardcore *(manual)* |

---

## Files

| File | Purpose |
|---|---|
| `achievement_tracker.py` | Main GUI application |
| `dun_parser.py` | Save-file decompressor and binary parser |
| `_ach_manual.json` | Auto-created; stores your manual checkbox state |
