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

These two endgame metas are **not** Steam bitmap achievements. The tracker verifies them from **beaten level flags** in your `.dun` file (difficulty bitmask bits 10 = Nightmare HC, 11 = Ruthless HC).

In **Chiku Guide** or **Meta Path** sort, each section includes a prominent **EXPAND** button listing every required map with done/missing status. The list follows your **Filter** (All / Completed / Missing).

### Ruthless Defender

| | |
|---|---|
| **Difficulty** | Ruthless |
| **Mode** | Hardcore (required on every map) |
| **Total** | 26 clears — 13 campaign maps + 13 challenges |

**Campaign (13)**

1. The Deeper Well  
2. Foundries and Forges  
3. Magus Quarters  
4. Alchemical Laboratory  
5. Servants Quarters  
6. Castle Armory  
7. Hall of Court  
8. The Throne Room  
9. Royal Gardens  
10. The Ramparts  
11. Endless Spires  
12. The Summit  
13. Glitterhelm Caverns  

**Challenges (13)**

1. No Towers Allowed  
2. Unlikely Allies  
3. Warping Core  
4. Raining Goblins  
5. Wizardry  
6. Ogre Crush  
7. Zippy Terror  
8. Chicken  
9. Moving Core  
10. Death From Above  
11. Assault  
12. Treasure Hunt  
13. Monster Fest  

All 26 must be cleared on **Ruthless Hardcore**. The tracker uses vanilla save tags from `DefaultDunDef.ini` (e.g. `SPECMQ` = Warping Core, `SPECES`/`SPECTS` = Assault/Treasure Hunt).

### Chromatic Defender

| | |
|---|---|
| **Difficulty** | Nightmare (Ruthless HC also counts) |
| **Mode** | Hardcore (required on every map) |
| **Prerequisite** | Ruthless Defender complete |
| **Total** | 30 clears — Lost Quests tab + DDT challenge tab |

**Required maps & challenges (30)**

1. Spooktacular Bay  
2. Challenge: Halloween Invasion  
3. The Striking Tree  
4. Challenge: Tavern Incursion  
5. Lover's Paradise  
6. Crystal Escort: Wandering Heart  
7. Lifestream Hollow  
8. Challenge: Forest Ogre Crush  
9. Tropics of Etheria  
10. Crystal Cave  
11. No Towers Allowed: Crystal Cave  
12. Challenge: Eternia Gauntlet  
13. Frostdale Wonderland  
14. Challenge: The Love Machine  
15. Tinkerer's Workshop  
16. Challenge: Workshop Assault  
17. Sky Spooktacular  
18. Frostdale Royal Court  
19. Challenge: Scorched Arabia  
20. Warping Core Challenge Pack 2: Part 1  
21. Warping Core Challenge Pack 2: Part 2  
22. Warping Core Challenge Pack 2: Part 3  
23. Jester's Spooktacular  
24. Valentine Citadel  
25. Return to Mistymire  
26. Return to Moraggo  
27. Return to Aquanos  
28. Return to Sky City  
29. Return to Crystalline Dimension  
30. Boss Rush II  

**Notes**

- DLC ownership is not checked — only whether the save records a NM/Ruthless HC clear for each map tag.
- Some Redux/legacy saves use alternate tags; the tracker also accepts `SPECCA` for Spooktacular Bay and `SPECGC` for Boss Rush II when the primary tag is unset.

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

## Local config (gitignored)

The app creates `_ach_manual.json` beside the script for **UI settings only** (last `.dun` path, `.ini` path, sort mode). This file can contain **absolute paths to your PC** — it is listed in `.gitignore` and is never pushed to the repo.

**Do not commit:** `.dun` save files, `_ach_manual.json`, or debug dumps derived from your save.

---

## Files

| File | Purpose |
|---|---|
| `achievement_tracker.pyw` | **Double-click to launch** on Windows (no console) |
| `achievement_tracker.py` | Main GUI application |
| `dun_parser.py` | Save-file decompressor, achievement bytes, beaten-level parser |
| `dump_ach_bytes.py` | Debug helper for inspecting raw achievement bytes |
| `.gitignore` | Excludes saves, local UI config, and debug dumps |
| `_ach_manual.json` | Auto-created local UI settings (**gitignored**) |
