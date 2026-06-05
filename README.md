# DD1 Achievement Tracker

A desktop GUI and **browser web app** for tracking all **163 Dungeon Defenders 1 achievements** — **118 Steam achievements** read from your save file, plus **45 non-Steam (CDT/DDT) entries** that are not stored in the `.dun` bitmap.

---

## Desktop vs Web

| | **Desktop** (`achievement_tracker.py`) | **Web** (`web/`) |
|---|---|---|
| Run | Python + PySide6 | Any modern browser |
| Save file | Browse to `.dun`; path remembered in `_ach_manual.json` | Drop or Browse — **parsed locally in your browser** |
| Upload | Never leaves your PC | **Never uploaded** — no server-side parsing |
| Steam index | Bundled JSON or auto INI from install path | Bundled `steam_achievement_index.json` |
| Account reset | Follows **save file**, not Steam profile | Same — save is source of truth |

### Web (Cloudflare Pages)

Static site in `web/` — deploy to **Cloudflare Pages** (free tier friendly: only static assets, zero Worker CPU per user).

**Build settings (dashboard):**

| Setting | Value |
|---|---|
| Build command | `python scripts/export_web_data.py && cd web && npm ci && npm run build` |
| Build output directory | `web/dist` |
| Root directory | repository root |

**Privacy:** Your `.dun` is read with `FileReader` in the tab only; it is **not** sent to Cloudflare or any backend.

**Live URL:** Set your custom domain in Cloudflare Pages after connecting this repo (e.g. `achievements.yourdomain.com`).

Local dev:

```bash
python scripts/export_web_data.py
cd web && npm install && npm run dev
```

---

## Features

- **Browse any `.dun` file** — point at your save (or someone else's) with **Browse…**; path is remembered locally
- **Steam achievements** — unlocked flags parsed from your `.dun` save (byte index mapped via bundled `steam_achievement_index.json`, or your game’s `UDKEngineSteamworks.ini` when on a standard install path)
- **Save-verified meta tracking** — **Ruthless Defender** and **Chromatic Defender** progress computed from beaten-level data in your save (no manual checkboxes)
- **5 clickable meta cards** at the top (Legendary → Ultimate → Eternal → Ruthless → Chromatic) with colored progress bars — **click a card to jump** to that section in **Meta Path** sort (scrolls so the section header is pinned to the top of the list)
- **Expandable map lists** for Ruthless and Chromatic sections — large expand buttons show every required map as done/missing (respects the active filter)
- **Dual progress headers** for Ruthless and Chromatic — section titles show both meta trophy status and map checklist progress, e.g. `RUTHLESS DEFENDER — 0/1 done (5/26 maps done)`
- **Sort modes** — **Chiku Guide** (recommended hunt order), **Meta Path** (Legendary → Chromatic ladder), or **Default** (by category)
- **Filter:** **All / Completed / Missing** plus real-time search
- **Color-coded accent bars** on each row show which meta path an achievement contributes to
- **Tips & stack hints** on rows (Chiku guide notes where available)
- **Clickable rows** open the achievement's [wiki.gg](https://dungeondefenders.wiki.gg) page

---

## Requirements

- Python 3.10 or newer
- Dependencies in `requirements.txt` (PySide6)

```
pip install -r requirements.txt
```

This repo is **self-contained** — clone it, install PySide6, point at a `.dun` file, and run. No Steam library scan, no parent monorepo, no game install required (only your save file).

---

## Quick start

```bash
git clone https://github.com/MrVokerr/DD1-Achievement-Tracker.git
cd DD1-Achievement-Tracker
pip install -r requirements.txt
python achievement_tracker.py
```

On first launch, click **Browse…** and select `DunDefHeroes.dun` from any location (yours, a friend’s backup, a copied save, etc.). The path is saved locally in `_ach_manual.json` for next time.

Use **Reload** after playing to refresh unlocks and map completion data.

### How data is loaded

| Data | Source |
|---|---|
| Steam achievement unlocks | 500-byte block inside your `.dun` file |
| Achievement byte → Steam ID order | `steam_achievement_index.json` (bundled), or `UDKEngineSteamworks.ini` auto-derived when your `.dun` lives under `…/Binaries/Win32` or `Win64` |
| Ruthless / Chromatic map progress | Beaten-level flags inside your `.dun` file |

You never need to browse for the INI manually on a normal install — if the save is under `Dungeon Defenders/Binaries/…`, the tracker finds the matching INI. Otherwise the bundled index is used.

---

## Ruthless & Chromatic Defender (save-verified)

These two endgame metas are **not** Steam bitmap achievements. The tracker verifies them from **beaten level flags** in your `.dun` file (difficulty bitmask bits 10 = Nightmare HC, 11 = Ruthless HC).

In **Chiku Guide** or **Meta Path** sort, each section includes a prominent **EXPAND** button listing every required map with done/missing status. The list follows your **Filter** (All / Completed / Missing).

**Section headers** for these two metas use a combined format:

| Section | Header example |
|---|---|
| Ruthless Defender | `RUTHLESS DEFENDER — 0/1 done (5/26 maps done)` |
| Chromatic Defender | `CHROMATIC DEFENDER — 0/1 done (4/30 maps done)` |

- **0/1 done** — whether the save-verified meta achievement is complete.
- **(X/Y maps done)** — how many individual campaign/challenge maps are cleared at the required difficulty (26 Ruthless, 30 Chromatic).

Click any top meta card to jump; the matching section header scrolls to the **top** of the achievement list.

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

## Local config (keep private)

The app creates `_ach_manual.json` beside the script for **UI settings only** (last `.dun` path, `.ini` path, sort mode). This file can contain **absolute paths to your PC**.

**Do not commit or share:** `.dun` save files, `_ach_manual.json`, `achievement_tracker.pyw`, or debug dumps derived from your save.

---

## Files

| File | Purpose |
|---|---|
| `achievement_tracker.py` | Main GUI application — run with `python achievement_tracker.py` |
| `achievement_data.py` | Shared achievement constants (desktop + web export; no Qt) |
| `save_checks.py` | Ruthless/Chromatic + unlock helpers without Qt (parity tests) |
| `dun_parser.py` | Save-file decompressor, achievement bytes, beaten-level parser |
| `steam_achievement_index.json` | Bundled Steam achievement ID order (maps `.dun` byte indices) |
| `requirements.txt` | Python dependencies (`PySide6`) |
| `scripts/export_web_data.py` | Export JSON into `web/src/data/` before web build |
| `scripts/parity_test.py` | Compare desktop vs web parser on the same `.dun` |
| `web/` | Vite + TypeScript static site (client-side parsing via `pako`) |
| `dump_ach_bytes.py` | Debug helper: `python dump_ach_bytes.py path/to/DunDefHeroes.dun` |
| `extract_steam_index.py` | Maintainer tool to refresh `steam_achievement_index.json` from a game INI |
| `_ach_manual.json` | Auto-created local UI settings (created on first run; keep private) |

### Parity testing

```bash
python scripts/export_web_data.py
cd web && npm install
python scripts/parity_test.py path/to/DunDefHeroes.dun
python scripts/parity_fixture_test.py
```

Or run unit tests only: `cd web && npm test`
