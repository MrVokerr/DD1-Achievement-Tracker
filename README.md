# DD1 Achievement Tracker

A desktop GUI for tracking all **163 Dungeon Defenders 1 achievements** — **118 Steam achievements** read from your save file, plus **45 non-Steam (CDT/DDT) entries** that are not stored in the `.dun` bitmap.

---

## Features

- **Browse any `.dun` file** — point at your save (or someone else's) with **Browse…**; path is remembered locally
- **Steam achievements** — unlocked flags parsed from `DunDefHeroes.dun` + `UDKEngineSteamworks.ini`
- **Save-verified meta tracking** — **Ruthless Defender** and **Chromatic Defender** progress computed from beaten-level data in your save (no manual checkboxes)
- **5 clickable meta cards** at the top (Legendary → Ultimate → Eternal → Ruthless → Chromatic) with colored progress bars — **click a card to jump** to that section in **Meta Path** sort
- **Expandable map lists** for Ruthless and Chromatic sections — large expand buttons show every required map as done/missing (respects the active filter)
- **Sort modes** — **Chiku Guide** (recommended hunt order), **Meta Path** (Legendary → Chromatic ladder), or **Default** (by category)
- **Filter:** **All / Completed / Missing** plus real-time search
- **Color-coded accent bars** on each row show which meta path an achievement contributes to
- **Tips & stack hints** on rows (Chiku guide notes where available)
- **Clickable rows** open the achievement's [wiki.gg](https://dungeondefenders.wiki.gg) page

---

## Requirements

- Python 3.10 or newer
- PySide6

```
pip install PySide6
```

---

## Usage

**Double-click** `achievement_tracker.pyw` on Windows — opens the GUI with no console window.

Or from a terminal:

```
python achievement_tracker.py
```

On first launch, click **Browse…** and select your save file:

```
<SteamLibrary>\steamapps\common\Dungeon Defenders\Binaries\Win32\DunDefHeroes.dun
```

(or `Win64\DunDefHeroes.dun` on 64-bit installs)

The Steam achievement index is read from:

```
<SteamLibrary>\steamapps\common\Dungeon Defenders\UDKGame\Config\UDKEngineSteamworks.ini
```

Both paths are included with every Steam installation of the game. The app can also auto-detect installs on common Steam library drives when no saved path exists.

Use **Reload** after playing to refresh unlocks and map completion data.

---

## Ruthless & Chromatic Defender (save-verified)

These two endgame metas are **not** Steam bitmap achievements. The tracker verifies them from **beaten level flags** in your `.dun` file:

| Achievement | Requirement |
|---|---|
| **Ruthless Defender** | All 13 original campaign maps **and** 12 of 13 original challenges on **Ruthless Hardcore** |
| **Chromatic Defender** | Ruthless Defender complete, then Spooktacular Bay → Scorched Arabia **and** Warping Core II → Boss Rush II on **Nightmare Hardcore** (Ruthless HC also counts) |

In **Chiku Guide** or **Meta Path** sort, each section includes a prominent **EXPAND** button listing every map with done/missing status. The list follows your **Filter** (All / Completed / Missing).

---

## Non-Steam achievements (CDT / DDT)

45 achievements from the **Community Development Team (CDT)** and **DD Together (DDT)** updates are **not** written into the Steam achievement bytes in the save. They appear in the list for reference but show **Missing** unless the tracker can infer completion from save data (Ruthless/Chromatic only).

There are **no manual checkboxes** — the tracker does not guess completion for generic DDT manual trophies.

---

## Meta achievement ladder

| Achievement | How to earn |
|---|---|
| **Legendary Defender** | All 56 base-game Steam achievements |
| **Ultimate Defender** | Legendary Defender + Eternia Shards DLC Steam set |
| **Eternal Defender** | Ultimate Defender + all CDT Lost Quests on Nightmare |
| **Ruthless Defender** | Original campaign + challenges on Ruthless HC *(save-verified)* |
| **Chromatic Defender** | Ruthless Defender + DDT map chain on NM HC *(save-verified)* |

Top meta cards show prerequisite progress and missing items in tooltips. Click any card to scroll to its tracking section.

---

## Local config (not committed)

The app creates `_ach_manual.json` beside the script for **UI settings only** (last `.dun` path, `.ini` path, sort mode). This file can contain **absolute paths to your PC** — it is listed in `.gitignore` and must not be pushed to git.

**Never commit:** `.dun` saves, `_ach_manual.json`, or other machine-local paths.

---

## Files

| File | Purpose |
|---|---|
| `achievement_tracker.pyw` | **Double-click to launch** (no console) |
| `achievement_tracker.py` | Main GUI application |
| `dun_parser.py` | Save-file decompressor, achievement bytes, beaten-level parser |
| `dump_ach_bytes.py` | Debug helper for inspecting raw achievement bytes |
| `_ach_manual.json` | Auto-created local UI settings (**gitignored**) |
