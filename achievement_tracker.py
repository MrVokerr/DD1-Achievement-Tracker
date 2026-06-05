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

# ── Achievement data (name, description, category, steam_id) ─────────────────
# steam_id = None  →  non-Steam achievement (not in save file)
ACHIEVEMENTS = [
    # ── Equipment (indices 0-2, 6, 44-45, 53) ────────────────────────────────
    ("Smithy",                              "You upgraded your first equipment. Keep it up!",                            "Equipment",     "ACH_SMITHY"),
    ("And This Is My Weapon",               "You upgraded an Equipment to its maximum potential!",                       "Equipment",     "ACH_MY_WEAPON"),
    ("Obedience Training",                  "Raise a Pet to its maximum potential.",                                     "Equipment",     "ACH_OBEDIENCE"),
    # ── Character Advancement (indices 3-5, 52, 55) ──────────────────────────
    ("Pupil",                               "Reached Hero Level 10.",                                                    "Advancement",   "ACH_PUPIL"),
    ("Veteran",                             "Reached Hero Level 30.",                                                    "Advancement",   "ACH_VETERAN"),
    ("Defender of Etheria",                 "Reached Hero Level 70.",                                                    "Advancement",   "ACH_ETHERIA"),
    # ── Equipment continued ───────────────────────────────────────────────────
    ("To The Limit",                        "Wore a completed set of maximum level Equipments.",                         "Equipment",     "ACH_LIMIT"),
    # ── Campaign (indices 7-18, 50-51) ───────────────────────────────────────
    ("From the Depths",                     "Completed all Area 1 levels on any difficulty setting.",                    "Campaign",      "ACH_DEPTHS"),
    ("To the Rooftops",                     "Completed all Area 2 levels on any difficulty setting.",                    "Campaign",      "ACH_ROOFTOPS"),
    ("A Taste of Victory",                  "Completed all Area 3 levels on any difficulty setting.",                    "Campaign",      "ACH_VICTORY"),
    ("Dungeon Crawler",                     "Completed all original campaign levels on any difficulty setting.",         "Campaign",      "ACH_CRAWLER"),
    ("The Belly of the Beast",              "Completed all Area 1 levels on Hard.",                                      "Campaign",      "ACH_BELLY"),
    ("The Body of the Beast",               "Completed all Area 2 levels on Hard.",                                      "Campaign",      "ACH_BODY"),
    ("The Crown of the Beast",              "Completed all Area 3 levels on Hard.",                                      "Campaign",      "ACH_CROWN"),
    ("Dungeon Raider (Campaign)",            "Completed all original campaign levels on Hard.",                           "Campaign",      "ACH_RAIDER"),
    ("From Fire with Brimstone",            "Completed all Area 1 levels on Insane.",                                    "Campaign",      "ACH_BRIMSTONE"),
    ("Through The Crowded Keep",            "Completed all Area 2 levels on Insane.",                                    "Campaign",      "ACH_KEEP"),
    ("To the Lofty Summit",                 "Completed all Area 3 levels on Insane.",                                    "Campaign",      "ACH_SUMMIT"),
    ("Dungeon Defender",                    "Completed all original campaign levels on Insane!",                         "Campaign",      "ACH_DEFENDER"),
    # ── Challenges (indices 19-37) ────────────────────────────────────────────
    ("Where's The Blueprints?",             "Completed No Towers Allowed on at least Medium Difficulty.",                "Challenges",    "ACH_BLUEPRINT"),
    ("Friends Forever",                     "Completed Unlikely Allies on at least Medium Difficulty.",                  "Challenges",    "ACH_FRIENDS"),
    ("88 Core",                             "Completed Warping Core on at least Medium Difficulty.",                     "Challenges",    "ACH_CORE"),
    ("Ella, Ella",                          "Completed Raining Goblins on at least Medium Difficulty.",                  "Challenges",    "ACH_ELLA"),
    ("Wizard Hunter",                       "Completed Wizardry on at least Medium Difficulty.",                         "Challenges",    "ACH_WIZARD"),
    ("You No Take Mushroom",                "Completed Ogre Crush on at least Medium Difficulty.",                       "Challenges",    "ACH_MUSHROOM"),
    ("Speed Freak",                         "Completed Zippy Terror on at least Medium Difficulty.",                     "Challenges",    "ACH_FREAK"),
    ("In A Fowl Mood",                      "Completed Chicken on at least Medium Difficulty.",                          "Challenges",    "ACH_FOWL"),
    ("Core Cardio",                         "Completed Moving Core on at least Medium Difficulty.",                      "Challenges",    "ACH_CARDIO"),
    ("Monster Mania",                       "Completed Death From Above on at least Medium Difficulty.",                 "Challenges",    "ACH_MANIA"),
    ("Core Destroyer",                      "Completed Assault on at least Medium Difficulty.",                          "Challenges",    "ACH_DESTROYER"),
    ("Gold Rush",                           "Completed Treasure Hunt on at least Medium Difficulty.",                    "Challenges",    "ACH_GOLD"),
    ("A Challenger Approaches",             "Completed all Challenges on Insane Difficulty!",                            "Challenges",    "ACH_CHALLANGER"),
    ("Weapon Master",                       "Completed No Towers Allowed on Insane Difficulty.",                         "Challenges",    "ACH_WEAPON"),
    ("Kobold Exterminator",                 "Completed Zippy Terror on Insane Difficulty.",                              "Challenges",    "ACH_EXTERMINATOR"),
    ("Monster Madness",                     "Completed Death From Above on Insane Difficulty.",                          "Challenges",    "ACH_MADNESS"),
    ("Dancing in the Rain",                 "Completed Raining Goblins on Insane Difficulty.",                           "Challenges",    "ACH_DANCING"),
    ("Gold Blitz",                          "Completed Treasure Hunt on Insane Difficulty.",                             "Challenges",    "ACH_BLITZ"),
    ("Ogre Block Party",                    "Completed Ogre Crush on Insane Difficulty.",                                "Challenges",    "ACH_BLOCK"),
    # ── Survival (indices 38-42, 73) ─────────────────────────────────────────
    ("Survivalist",                         "Reached Survival Wave 15 on at least Medium Difficulty.",                   "Survival",      "ACH_SURVIVALIST"),
    ("Thick Skin",                          "Reached Survival Wave 20 on at least Medium Difficulty.",                   "Survival",      "ACH_THICK"),
    ("Tough Guy",                           "Reached Survival Wave 15 on at least Hard Difficulty.",                     "Survival",      "ACH_TOUGH"),
    ("Iron Man",                            "Reached Survival Wave 10 on Insane Difficulty.",                            "Survival",      "ACH_IRONMAN"),
    ("Defense Is the Best Offense",         "Reached Wave 10 on all levels in Pure Strategy on at least Medium.",        "Survival",      "ACH_OFFENSE"),
    # ── Awards (indices 43, 46-49) ────────────────────────────────────────────
    ("True Nobility",                       "Earned the Lord Award on at least Medium Difficulty.",                      "Awards",        "ACH_NOBILITY"),
    # ── Equipment continued (indices 44-45) ──────────────────────────────────
    ("O Mighty Smiter!",                    "Wore a full set of Godly Items.",                                           "Equipment",     "ACH_SMITER"),
    ("Divine Intention",                    "Picked up a Godly Weapon.",                                                 "Equipment",     "ACH_DEVINE"),
    # ── Awards continued ─────────────────────────────────────────────────────
    ("Perfectionist",                       "Earned the Flawless Victory Award on every Mission on at least Medium.",    "Awards",        "ACH_PERFECTIONIST"),
    ("Daredevil",                           "Earned Skin of Your Teeth Award on 6 Missions.",                            "Awards",        "ACH_DAREDEVIL"),
    ("Mastermind",                          "Earned the Master Strategist Award on all Missions.",                       "Awards",        "ACH_MASTERMIND"),
    ("Brute Force",                         "Earned the Gunslinger Award on all Missions.",                              "Awards",        "ACH_FORCE"),
    # ── Campaign continued ────────────────────────────────────────────────────
    ("Team Effort",                         "Completed all levels with 4 active players on at least Medium Difficulty.", "Campaign",      "ACH_EFFORT"),
    ("A Matter of Perspective",             "Saw all four Hero endings (defeat Ancient Dragon 4 times).",                "Campaign",      "ACH_PERSPECTIVE"),
    # ── Advancement continued ─────────────────────────────────────────────────
    ("Group Hug",                           "Raised a Hero of each type to Level 70.",                                   "Advancement",   "ACH_HUG"),
    # ── Equipment continued ───────────────────────────────────────────────────
    ("Catch 'em All",                       "Stored all Pet types in your Item Box or on your Heroes.",                  "Equipment",     "ACH_CATCH"),
    # ── Misc ──────────────────────────────────────────────────────────────────
    ("Master Banker",                       "Stored 15,000,000 Mana in your Mana Bank.",                                 "Misc",          "ACH_BANKER"),
    # ── Advancement continued ─────────────────────────────────────────────────
    ("Good Student",                        "Completed the Tutorial. You deserve a cookie!",                             "Advancement",   "ACH_STUDENT"),
    # ── Meta: Base Game ───────────────────────────────────────────────────────
    ("Legendary Defender",                  "You have earned every Dungeon Defenders Accomplishment! Trendy salutes you!", "Meta",        "ACH_LEGENDARY"),
    # ── Seasonal: Etherian Holiday Extravaganza ───────────────────────────────
    ("Jingled All the Way",                 "Delivered all the presents, and saved Santa Tavernkeep from the vile clutches of Mega-Snowman!", "Seasonal", "ACH_XMAS"),
    # ── Eternia Shards: Part 1 (Mistymire) ───────────────────────────────────
    ("Eternia Shard Recovered: Purple",     "You retrieved the Purple Lost Eternia Shard from the depths of Mistymire Forest!", "Eternia Shards", "ACH_ETERNIASHARDS_PART1_ANY"),
    ("Nightmare Eternia Shard: Purple",     "You retrieved the Purple Lost Eternia Shard from Mistymire Forest... on Nightmare!", "Eternia Shards", "ACH_ETERNIASHARDS_PART1_NIGHTMARE"),
    ("Portal Protector",                    "You defended the portal against the rampaging Spider horde!",               "Eternia Shards", "ACH_PORTAL_PROTECTOR"),
    ("Nightmare Portal Protector",          "You defended the portal against the rampaging Spider horde... on Nightmare!", "Eternia Shards", "ACH_PORTAL_PROTECTOR_NIGHTMARE"),
    ("Mythical Defender",                   "You completed every mission in the original Campaign on Nightmare difficulty!", "Eternia Shards", "ACH_MYTHICAL_DEFENDER"),
    ("Hardcore Mythical Defender",          "You completed every original Campaign mission on Nightmare without dying.",  "Eternia Shards", "NEW_ACHIEVEMENT_9_2"),
    # ── Assault Mission Pack ──────────────────────────────────────────────────
    ("Dungeon Raider (Assault)",            "You completed every mission in the Assault Mission Pack!",                   "Assault Pack",  "NEW_ACHIEVEMENT_9_3"),
    ("Mythical Dungeon Raider",             "You completed every mission in the Assault Mission Pack on Nightmare!",      "Assault Pack",  "NEW_ACHIEVEMENT_9_4"),
    # ── Seasonal: Festival of Love ────────────────────────────────────────────
    ("Playin' Cupid",                       "You played matchmaker for the gender mobs on Sky O' Love and defeated Mega Cupid!", "Seasonal", "ACH_PLAYIN_CUPID"),
    ("Playin' Mythical Cupid",              "You played matchmaker for the gender mobs on Sky O' Love... on Nightmare!", "Seasonal",      "ACH_PLAYIN_CUPID_NIGHTMARE"),
    # ── Eternia Shards: Part 2 (Moraggo) ─────────────────────────────────────
    ("Transcendent Challenge Champion",     "You completed every original Challenge on Nightmare Hardcore difficulty.",   "Eternia Shards", "ACH_CHALLENGE_MYTHICAL_HARDCORE"),
    ("Eternia Shard Recovered: Blue",       "You retrieved the Blue Lost Eternia Shard from the scorching sands of Moraggo!", "Eternia Shards", "ACH_ETERNIASHARDS_PART2_ANY"),
    ("Djinn Recruiter",                     "You assembled an army to win the 'War of the Djinn' Challenge!",            "Eternia Shards", "ACH_DJINN_RECRUITER"),
    ("Nightmare Eternia Shard: Blue",       "You retrieved the Blue Lost Eternia Shard from Moraggo... on Nightmare!",   "Eternia Shards", "ACH_ETERNIASHARDS_PART2_NIGHTMARE"),
    ("Nightmare Djinn Recruiter",           "You assembled an army to win the 'War of the Djinn' Challenge... on Nightmare!", "Eternia Shards", "ACH_DJINN_RECRUITER_NIGHTMARE"),
    # ── Survival: Transcendent (index 73) ────────────────────────────────────
    ("Transcendent Survivalist",            "You achieved Nightmare Survival Victory on every Campaign mission (wave 25).", "Survival",     "ACH_TRANSCENDENT_SURVIVALIST"),
    # ── Eternia Shards: Part 3 (Aquanos) ─────────────────────────────────────
    ("Eternia Shard Recovered: Yellow",     "You retrieved the Yellow Lost Eternia Shard from the cold waters of Aquanos!", "Eternia Shards", "ACH_ETERNIASHARDS_PART3_ANY"),
    ("Puzzle Solver",                       "You solved the 'Riddle of the Deep' Challenge!",                            "Eternia Shards", "ACH_PUZZLE_SOLVER"),
    ("Nightmare Eternia Shard: Yellow",     "You retrieved the Yellow Lost Eternia Shard from Aquanos... on Nightmare!",  "Eternia Shards", "ACH_ETERNIASHARDS_PART3_NIGHTMARE"),
    ("Nightmare Puzzle Solver",             "You solved the 'Riddle of the Deep' Challenge... on Nightmare!",            "Eternia Shards", "ACH_PUZZLE_SOLVER_NIGHTMARE"),
    # ── Summoner Hero ─────────────────────────────────────────────────────────
    ("Real Time Strategist",                "Completed Campaign + 3 Eternia Shards using only summoned mobs and Overlord mode.", "Eternia Shards", "ACH_RTS"),
    ("Mythical Real Time Strategist",       "Same as Real Time Strategist but on Nightmare.",                            "Eternia Shards", "ACH_RTS_MYTHICAL"),
    # ── Eternia Shards: Part 4 (Sky City) ────────────────────────────────────
    ("Eternia Shard Recovered: Red",        "You retrieved the Red Lost Eternia Shard from the billowing clouds of Sky City!", "Eternia Shards", "ACH_ETERNIASHARDS_PART4_ANY"),
    ("Nightmare Eternia Shard: Red",        "You retrieved the Red Lost Eternia Shard from Sky City... on Nightmare!",   "Eternia Shards", "ACH_ETERNIASHARDS_PART4_NIGHTMARE"),
    ("Boss Crusher",                        "You completed the Boss Rush Challenge!",                                    "Eternia Shards", "ACH_BOSS_CRUSHER"),
    ("Nightmare Boss Crusher",              "You completed the Boss Rush Challenge... on Nightmare!",                    "Eternia Shards", "ACH_BOSS_CRUSHER_NIGHTMARE"),
    ("Heroes to the Rescue",               "You journeyed to the Crystalline Dimension, rescued the Legendary Heroes, and defeated an ultimate evil!", "Eternia Shards", "ACH_HEROES"),
    ("Nightmare Heroes to the Rescue",      "You journeyed to the Crystalline Dimension... on Nightmare!",               "Eternia Shards", "ACH_HEROES_NIGHTMARE"),
    # ── Meta: Ultimate Defender ───────────────────────────────────────────────
    ("I've Got Monsters in My Pocket",      "You collected every Pet in all Etheria in your Item Box!",                  "Meta",          "ACH_MONSTERS"),
    ("Ultimate Defender",                   "You earned every Dungeon Defenders Accomplishment through the Eternia Shards Campaign!", "Meta", "ACH_ULTIMATE_DEFENDER"),
    # ── Seasonal: Anniversary Pack ────────────────────────────────────────────
    ("Anniversary Defender",                "You defended your Tavern against the horde!",                               "Seasonal",      "ACH_ANNIVERSARY"),
    ("Nightmare Anniversary Defender",      "You defended your Tavern against the horde... on Nightmare!",               "Seasonal",      "ACH_ANNIVERSARY_NIGHTMARE"),
    # ── Seasonal: Halloween Spooktacular 2 ───────────────────────────────────
    ("Pumpkin Party",                       "You completed the Halloween Spooktacular 2 Challenge!",                     "Seasonal",      "ACH_PUMPKIN_PARTY"),
    ("Pumpkin Party Nightmare",             "You completed the Halloween Spooktacular 2 Challenge... on Nightmare!",     "Seasonal",      "ACH_PUMPKINPARTY_NIGHTMARE"),
    # ── Seasonal: The Greater Turkey Hunt ────────────────────────────────────
    ("Greater Turkey Hunter",               "You purged the ruins of Karathiki of all Turkey interlopers!",              "Seasonal",      "ACH_GREATER_TURKEYHUNTER"),
    ("Nightmare Greater Turkey Hunter",     "You purged the ruins of Karathiki of all Turkey interlopers... on Nightmare!", "Seasonal",   "ACH_GREATER_TURKEYHUNTER_NIGHTMARE"),
    # ── Seasonal: Silent Night ────────────────────────────────────────────────
    ("Not So Silent Night",                 "You delivered Santa's goodies... and then took on the big man himself!",    "Seasonal",      "ACH_SILENT_NIGHT"),
    ("Nightmare Not So Silent Night",       "You delivered Santa's goodies... and then took on the big man himself... on Nightmare!", "Seasonal", "ACH_SILENT_NIGHT_NIGHTMARE"),
    # ── Seasonal: Winter Wonderland ───────────────────────────────────────────
    ("Winter Wonderland",                   "You survived the onslaught of the Holiday Guardians!",                      "Seasonal",      "ACH_WINTER_WONDERLAND"),
    ("Nightmare Winter Wonderland",         "You survived the onslaught of the Holiday Guardians... on Nightmare!",      "Seasonal",      "ACH_WINTER_WONDERLAND_NIGHTMARE"),
    # ── Seasonal: Festival of Love (Anticupid) ────────────────────────────────
    ("Playin' Anticupid",                   "You successfully prevented hordes of mob matches in the Temple O' Love!",   "Seasonal",      "ACH_VDAY_2013"),
    ("Nightmare Playin' Anticupid",         "You successfully prevented hordes of mob matches in the Temple O' Love... on Nightmare!", "Seasonal", "ACH_VDAY_2013_NIGHTMARE"),
    # ── Tinkerer's Lab Mission Pack ───────────────────────────────────────────
    ("Tinkerer's Defender",                 "You Defended the Tinkerer's Lab and cleared the way for EV's upgrade!",    "Tinkerer's Lab", "ACH_LAB"),
    ("Nightmare Tinkerer's Defender",       "You Defended the Tinkerer's Lab and cleared the way for EV's upgrade... on Nightmare!", "Tinkerer's Lab", "ACH_LAB_NIGHTMARE"),
    ("EV Reprogrammer",                     "You assaulted the Lab and eliminated the squad of corrupted EV's!",        "Tinkerer's Lab", "ACH_LABASSAULT"),
    ("Nightmare EV Reprogrammer",           "You assaulted the Lab and eliminated the squad of corrupted EV's... on Nightmare!", "Tinkerer's Lab", "ACH_LABASSAULT_NIGHTMARE"),
    # ── CDT Lost Quests — Steam (indices 104-117) ─────────────────────────────
    ("Trial by Fire and Lightning",         "You ventured into the heart of Embermount, grounded the Harbingers and extinguished the flame of the mighty Phoenix!", "CDT Steam", "ACH_TRIAL_FIRELIGHT"),
    ("Nightmare Trial by Fire and Lightning","You ventured into the heart of Embermount... on Nightmare!",               "CDT Steam",     "ACH_TRIAL_FIRELIGHT_NIGHTMARE"),
    ("Out of this World",                   "You saved the moonbase from the enemy onslaught!",                         "CDT Steam",     "ACH_MOONBASE"),
    ("Nightmare Out of this World",         "You saved the moonbase from the enemy onslaught... on Nightmare!",         "CDT Steam",     "ACH_MOONBASE_NIGHTMARE"),
    ("Hero of Water",                       "You journeyed deep into the ocean and reclaimed the legendary Temple of Water!", "CDT Steam", "ACH_TEMPLE_WATER"),
    ("Nightmare Hero of Water",             "You journeyed deep into the ocean and reclaimed the Temple of Water... on Nightmare!", "CDT Steam", "ACH_TEMPLE_WATER_NIGHTMARE"),
    ("Swashbuckler",                        "You successfully defended Buccaneer Bay!",                                  "CDT Steam",     "ACH_BUCCANEER_BAY"),
    ("Nightmare Swashbuckler",              "You successfully defended Buccaneer Bay... on Nightmare!",                  "CDT Steam",     "ACH_BUCCANEER_BAY_NIGHTMARE"),
    ("Crystalline Resurgence",              "You did battle once more in the Crystalline lands (complete 3 parts of the series).", "CDT Steam", "ACH_CR"),
    ("Nightmare Crystalline Resurgence",    "You did battle once more in the Crystalline lands... on Nightmare!",        "CDT Steam",     "ACH_CR_NIGHTMARE"),
    ("Nightmare A Very Misty Christmas",    "You returned to Mistymire for a very special celebration... on Nightmare!", "CDT Steam",     "ACH_WM_NIGHTMARE"),
    ("Nightmare Exterminator",              "You ventured deep into the Infested Ruins and drove out the monstrous infestation of wasps... on Nightmare!", "CDT Steam", "ACH_IF_NIGHTMARE"),
    ("Nightmare Slayer of Omenak",          "You defended the ancient Omenak Cathedral from the goblin hordes and their Flying Mech... on Nightmare!", "CDT Steam", "ACH_OME_NIGHTMARE"),
    ("Nightmare Tomb of Etheria",           "You dared to raid the Tomb of Etheria, and lived to tell the tale... on Nightmare!", "CDT Steam", "ACH_TOMB_NIGHTMARE"),
    # ── CDT Lost Quests — Non-Steam (manual checkbox) ────────────────────────
    ("Nightmare Soothing Dungeoneer",       "You successfully defended the Dread Dungeon and made it calm once more... on Nightmare!", "CDT Manual", None),
    ("Nightmare Successful Librarian",      "You successfully defended the Arcane Library precious knowledge... on Nightmare!", "CDT Manual", None),
    ("Nightmare Pirate Defender",           "You successfully defended the crystals against hordes of pirates... on Nightmare!", "CDT Manual", None),
    ("Coastal Merchant",                    "You successfully defended Coastal Bazaar!",                                 "CDT Manual",    None),
    ("Nightmare Coastal Merchant",          "You successfully defended Coastal Bazaar... on Nightmare!",                 "CDT Manual",    None),
    ("Nightmare Phoenix Handler",           "You prevented multiple waves of phoenixes rebirths... on Nightmare!",       "CDT Manual",    None),
    ("Nightmare Polybius Invader",          "You successfully assaulted the Temple of Polybius... on Nightmare!",        "CDT Manual",    None),
    ("Nightmare Egg Escorter",              "You successfully escorted the Egg Basket... on Nightmare!",                 "CDT Manual",    None),
    ("Nightmare Emerald Explorer",          "You successfully defended the Emerald City against the Desert Cupid... on Nightmare!", "CDT Manual", None),
    ("Nightmare Magus Citizen",             "You successfully stopped the Crazy Apprentice and his towers... on Nightmare!", "CDT Manual", None),
    # ── Meta: Eternal Defender ────────────────────────────────────────────────
    ("Eternal Defender",                    "After achieving Ultimate Defender, you cleared every Lost Quests map on Nightmare! (Non-Steam)", "Meta", None),
    # ── DDT Updates — Non-Steam (manual checkbox) ─────────────────────────────
    ("Spooky Swashbuckler",                 "You successfully defended Spooktacular Bay!",                               "DDT Manual",    None),
    ("Nightmare Spooky Swashbuckler",       "You successfully defended Spooktacular Bay... on Nightmare!",               "DDT Manual",    None),
    ("Halloween Defender",                  "You successfully cleared all of the spooky waves!",                         "DDT Manual",    None),
    ("Nightmare Halloween Defender",        "You successfully cleared all of the spooky waves... on Nightmare!",         "DDT Manual",    None),
    ("Nature Enthusiast",                   "You successfully stopped the Emerald Monk from disrupting The Striking Tree!", "DDT Manual",  None),
    ("Nightmare Nature Enthusiast",         "You successfully stopped the Emerald Monk from disrupting The Striking Tree... on Nightmare!", "DDT Manual", None),
    ("Tavern Defender",                     "You defended the Tavern gloriously once again!",                            "DDT Manual",    None),
    ("Nightmare Tavern Defender",           "You defended the Tavern gloriously once again... on Nightmare!",            "DDT Manual",    None),
    ("Love Defender",                       "You successfully returned to Lover's Paradise and defended it from the couples!", "DDT Manual", None),
    ("Nightmare Love Defender",             "You successfully returned to Lover's Paradise and defended it from the couples... on Nightmare!", "DDT Manual", None),
    ("Heart Wanderer",                      "You successfully escorted the heart!",                                      "DDT Manual",    None),
    ("Nightmare Heart Wanderer",            "You successfully escorted the heart... on Nightmare!",                      "DDT Manual",    None),
    ("Lifestream Hollow Defender",          "You successfully protected the Lifestream from hordes of enemies.",         "DDT Manual",    None),
    ("Nightmare Lifestream Hollow Defender","You successfully protected the Lifestream from hordes of enemies... on Nightmare!", "DDT Manual", None),
    ("Forest Ogre Crusher",                 "You successfully defeated the powerful Ogres.",                             "DDT Manual",    None),
    ("Nightmare Forest Ogre Crusher",       "You successfully defeated the powerful Ogres... on Nightmare!",             "DDT Manual",    None),
    # ── Meta: Ruthless Defender ───────────────────────────────────────────────
    ("Ruthless Defender",                   "You successfully beat the original campaign and challenges... on Ruthless Hardcore! (Non-Steam)", "Meta", None),
    # ── DDT continued ─────────────────────────────────────────────────────────
    ("Nightmare Jester's Spooktacular Trick-o-Treater", "You successfully beat the trick-o-treaters... on Nightmare!", "DDT Manual", None),
    ("Nightmare Frostdale Christmas Defender","You successfully defended Christmas again... on Nightmare!",              "DDT Manual",    None),
    ("Nightmare Valentine Citadel Lover",   "You successfully saved Valentine... on Nightmare!",                         "DDT Manual",    None),
    ("Nightmare Love Machine Worker",       "You successfully let the Love Machine run... on Nightmare!",                "DDT Manual",    None),
    ("Returnia Part 1",                     "You successfully returned to Mistymire and defended it once again.",        "DDT Manual",    None),
    ("Returnia Part 2",                     "You successfully returned to Moraggo and defended it once again.",          "DDT Manual",    None),
    ("Returnia Part 3",                     "You successfully returned to Aquanos and defended it once again.",          "DDT Manual",    None),
    ("Returnia Part 4",                     "You successfully returned to Sky City and defended it once again.",         "DDT Manual",    None),
    ("Returnia Part 5",                     "You successfully returned to the Crystalline Dimension and defended it once again.", "DDT Manual", None),
    ("Nightmare Workshop Defender",         "You successfully investigated the workshop... on Nightmare!",               "DDT Manual",    None),
    ("Nightmare Workshop Dweller",          "You successfully prevented the theft of technology... on Nightmare!",       "DDT Manual",    None),
    ("Nightmare Sky Trick O'Treater",       "You successfully defended this Sky Island against the ominous watchers... on Nightmare!", "DDT Manual", None),
    ("Nightmare Royal Helper",              "You successfully defended the Royal Court from the festive enemies... on Nightmare!", "DDT Manual", None),
    ("Nightmare Scorched Defender",         "You successfully defended the volcano desert town... on Nightmare!",        "DDT Manual",    None),
    ("Nightmare Boss Rusher",               "You successfully fought your way through all gauntlets... on Nightmare!",   "DDT Manual",    None),
    # ── Meta: Chromatic Defender ──────────────────────────────────────────────
    ("Chromatic Defender",                  "After becoming Ruthless Defender, beat all maps Spooktacular Bay→Scorched Arabia + Warping Core II→Boss Rush II on Nightmare Hardcore! (Non-Steam)", "Meta", None),
    # ── DDT continued ─────────────────────────────────────────────────────────
    ("Nightmare Revenge Lover",             "You successfully prevented the hordes of lovers from enacting their revenge... on Nightmare!", "DDT Manual", None),
]

# ── Lookup tables ─────────────────────────────────────────────────────────────
STEAM_ID_MAP     = {row[3]: row[0] for row in ACHIEVEMENTS if row[3]}
_NAME_TO_STEAMID = {row[0]: row[3] for row in ACHIEVEMENTS if row[3]}

# ── Meta achievement requirements ─────────────────────────────────────────────
_LEGENDARY_REQS = [
    "Smithy", "And This Is My Weapon", "Obedience Training",
    "Pupil", "Veteran", "Defender of Etheria",
    "To The Limit",
    "From the Depths", "To the Rooftops", "A Taste of Victory", "Dungeon Crawler",
    "The Belly of the Beast", "The Body of the Beast", "The Crown of the Beast",
    "Dungeon Raider (Campaign)",
    "From Fire with Brimstone", "Through The Crowded Keep", "To the Lofty Summit",
    "Dungeon Defender",
    "Where's The Blueprints?", "Friends Forever", "88 Core", "Ella, Ella",
    "Wizard Hunter", "You No Take Mushroom", "Speed Freak", "In A Fowl Mood",
    "Core Cardio", "Monster Mania", "Core Destroyer", "Gold Rush",
    "A Challenger Approaches", "Weapon Master", "Kobold Exterminator",
    "Monster Madness", "Dancing in the Rain", "Gold Blitz", "Ogre Block Party",
    "Survivalist", "Thick Skin", "Tough Guy", "Iron Man",
    "Defense Is the Best Offense",
    "True Nobility", "O Mighty Smiter!", "Divine Intention",
    "Perfectionist", "Daredevil", "Mastermind", "Brute Force",
    "Team Effort", "A Matter of Perspective",
    "Group Hug", "Catch 'em All", "Master Banker", "Good Student",
]

_ULTIMATE_REQS = [
    "Legendary Defender",
    "Jingled All the Way",
    "Portal Protector", "Nightmare Portal Protector",
    "Eternia Shard Recovered: Purple", "Nightmare Eternia Shard: Purple",
    "Mythical Defender", "Hardcore Mythical Defender",
    "Dungeon Raider (Assault)", "Mythical Dungeon Raider",
    "Playin' Cupid", "Playin' Mythical Cupid",
    "Transcendent Challenge Champion",
    "Eternia Shard Recovered: Blue", "Nightmare Eternia Shard: Blue",
    "Djinn Recruiter", "Nightmare Djinn Recruiter",
    "Transcendent Survivalist",
    "Eternia Shard Recovered: Yellow", "Nightmare Eternia Shard: Yellow",
    "Puzzle Solver", "Nightmare Puzzle Solver",
    "Real Time Strategist", "Mythical Real Time Strategist",
    "Eternia Shard Recovered: Red", "Nightmare Eternia Shard: Red",
    "Boss Crusher", "Nightmare Boss Crusher",
    "Heroes to the Rescue", "Nightmare Heroes to the Rescue",
    "I've Got Monsters in My Pocket",
]

_ETERNAL_REQS = [
    "Ultimate Defender",
    "Nightmare Trial by Fire and Lightning",
    "Nightmare Out of this World",
    "Nightmare Hero of Water",
    "Nightmare Swashbuckler",
    "Nightmare Crystalline Resurgence",
    "Nightmare A Very Misty Christmas",
    "Nightmare Exterminator",
    "Nightmare Slayer of Omenak",
    "Nightmare Tomb of Etheria",
    "Nightmare Soothing Dungeoneer",
    "Nightmare Successful Librarian",
    "Nightmare Pirate Defender",
    "Nightmare Coastal Merchant",
    "Nightmare Phoenix Handler",
    "Nightmare Polybius Invader",
    "Nightmare Egg Escorter",
    "Nightmare Emerald Explorer",
    "Nightmare Magus Citizen",
]

# (title, steam_id_of_self_or_None, prereq_list, accent_color)
META_DEFS = [
    ("Legendary Defender",  "ACH_LEGENDARY",        _LEGENDARY_REQS, "#9b59b6"),
    ("Ultimate Defender",   "ACH_ULTIMATE_DEFENDER", _ULTIMATE_REQS,  "#f39c12"),
    ("Eternal Defender",    None,                    _ETERNAL_REQS,   "#1abc9c"),
    ("Ruthless Defender",   None,                    [],              "#e74c3c"),
    ("Chromatic Defender",  None,                    [],              "#3498db"),
]

_META_SECTION_KEYS = {
    "Legendary Defender": "legendary",
    "Ultimate Defender": "ultimate",
    "Eternal Defender": "eternal",
    "Ruthless Defender": "ruthless",
    "Chromatic Defender": "chromatic",
}

RUTHLESS_CAMPAIGN_MAPS: list[tuple[str, str]] = [
    ("CAMPDW", "The Deeper Well"), ("CAMPFF", "Foundries and Forges"), ("CAMPMQ", "Magus Quarters"),
    ("CAMPAL", "Alchemical Laboratory"), ("CAMPSQ", "Servants Quarters"), ("CAMPCA", "Castle Armory"),
    ("CAMPHC", "Hall of Court"), ("CAMPTR", "The Throne Room"), ("CAMPRG", "Royal Gardens"),
    ("CAMPRP", "The Ramparts"), ("CAMPES", "Endless Spires"), ("CAMPTS", "The Summit"),
    ("CAMPGC", "Glitterhelm Caverns"),
]
# Vanilla challenge tags from DefaultDunDef.ini (SPECAL=Raining Goblins, SPECTR=Chicken, etc.)
RUTHLESS_CHALLENGE_MAPS: list[tuple[str, str]] = [
    ("SPECDW", "No Towers Allowed"), ("SPECFF", "Unlikely Allies"), ("SPECMQ", "Warping Core"),
    ("SPECAL", "Raining Goblins"), ("SPECSQ", "Wizardry"), ("SPECCA", "Ogre Crush"),
    ("SPECHC", "Zippy Terror"), ("SPECTR", "Chicken"), ("SPECRG", "Moving Core"),
    ("SPECRP", "Death From Above"), ("SPECES", "Assault"), ("SPECTS", "Treasure Hunt"),
    ("SPECGC", "Monster Fest"),
]
# Lost Quests tab + challenge tab maps for Chromatic Defender (Guides/wiki_clean/Chromatic Defender.md)
CHROMATIC_MAPS: list[tuple[str, str]] = [
    ("LHOLOC", "Spooktacular Bay"),
    ("CDHUNT", "Challenge: Halloween Invasion"),
    ("VDAY04", "The Striking Tree"),
    ("CAMPHP", "Challenge: Tavern Incursion"),
    ("SPECTI", "Lover's Paradise"),
    ("VDAY03", "Crystal Escort: Wandering Heart"),
    ("LIFHOL", "Lifestream Hollow"),
    ("WRPAR", "Challenge: Forest Ogre Crush"),
    ("TROPI0D", "Tropics of Etheria"),
    ("CDCAVE", "Crystal Cave"),
    ("NTACC", "No Towers Allowed: Crystal Cave"),
    ("WWEHE", "Challenge: Eternia Gauntlet"),
    ("CDTSBB", "Frostdale Wonderland"),
    ("CDTTWC", "Challenge: The Love Machine"),
    ("CAMPTL", "Tinkerer's Workshop"),
    ("CDTTWA", "Challenge: Workshop Assault"),
    ("SKYSPK", "Sky Spooktacular"),
    ("DTSIL", "Frostdale Royal Court"),
    ("CDTARC", "Challenge: Scorched Arabia"),
    ("WRPARC", "Warping Core Challenge Pack 2: Part 1"),
    ("CDTAQA", "Warping Core Challenge Pack 2: Part 2"),
    ("WRPOMN", "Warping Core Challenge Pack 2: Part 3"),
    ("JSTSPK", "Jester's Spooktacular"),
    ("MAGUSV", "Valentine Citadel"),
    ("RETMIS", "Return to Mistymire"),
    ("RETMOR", "Return to Moraggo"),
    ("RETAQU", "Return to Aquanos"),
    ("RETSKY", "Return to Sky City"),
    ("RETCRD", "Return to Crystalline Dimension"),
    ("DDTBR2", "Boss Rush II"),
]
# Redux / legacy save tags that also satisfy a primary Chromatic map entry
CHROMATIC_ALT_TAGS: dict[str, tuple[str, ...]] = {
    "LHOLOC": ("SPECCA",),  # Redux records Spooktacular Bay under legacy Ogre Crush tag
    "DDTBR2": ("SPECGC",),
}

_RUTHLESS_HC_BIT = 1 << 11
_NM_HC_BIT = 1 << 10

# ── Chiku guide hunt order (Guides/Chiku's Dungeon Defenders Achievements Guide.md)
CHIKU_SECTIONS: list[tuple[str, str, str]] = [
    ("intro", "Introduction",
     "Tutorial and tavern-core checks (F) for per-map award progress."),
    ("campaign_stack", "Campaign Megastack — Deeper Well → Glitterhelm",
     "Chiku NM HC stack: 4 splitscreen heroes, hero-only (Gunslinger), flawless core after wave 1, "
     "no deaths — Brute Force + Perfectionist + Team Effort + Mythical/Hardcore Mythical Defender + campaign clears."),
    ("campaign_awards", "Campaign Awards — Cleanup",
     "Daredevil: chip core to ≤100 HP on wave 1 only (6 maps), then flawless. "
     "Mastermind pairs with Mythical RTS (tower final wave only). Perspective: 4 Summit runs."),
    ("campaign_diff", "Campaign Difficulty Trophies",
     "Area Hard/Insane/Any clears — NM runs do not retroactively grant Hard/Insane area achievements."),
    ("free", "Free Achievements & Economy",
     "Earn passively while upgrading gear, leveling heroes, and banking mana."),
    ("challenges", "Main Campaign Challenges",
     "All 12 original challenges on NM HC → Transcendent Challenge Champion + tiered challenge trophies."),
    ("survival", "Survival & Pure Strategy",
     "Transcendent Survivalist (wave 24, lose 25) also completes Survivalist / Thick Skin / Tough Guy / Iron Man."),
    ("pets", "Pet Achievements",
     "31 pets — mostly survival wave 25; Sky of Love, Assault Pack, Summit guardians, Presidential Royale."),
    ("shards", "Summoner & Eternia Shards",
     "Mythical RTS on campaign + Mistymire/Moraggo/Aquanos; Sky City shard separate. Mastermind stacks if towers only on final wave."),
    ("ultimate_dlc", "Ultimate Defender — Seasonal & Assault",
     "Jingled All the Way, Assault Pack, Sky o' Love — often done during pet/survival farming."),
    ("meta_ud", "Meta — Ultimate & Legendary Defender",
     "Legendary = base game; Ultimate = Legendary + Eternia Shards DLC set."),
    ("eternal", "Eternal Defender — Lost Quests",
     "After Ultimate: all listed Lost Quest maps on Nightmare (manual CDT/DDT entries included)."),
    ("ddt_manual", "DDT Manual Achievements",
     "Post-Eternal content — not stored in Steam save."),
    ("ruthless", "Ruthless Defender",
     "Late game: original campaign + all 13 challenges on Ruthless HC (~6k+ tower stats)."),
    ("chromatic", "Chromatic Defender",
     "After Ruthless: all 30 Lost Quest / DDT maps on NM HC (Ruthless HC also counts)."),
    ("extras", "Seasonal & DLC Extras",
     "Not required for Ultimate/Eternal — holiday packs, Tinkerer's Lab, etc."),
]

CHIKU_SECTION_MEMBERS: dict[str, list[str]] = {
    "intro": ["Good Student"],
    "campaign_stack": [
        "Brute Force", "Perfectionist", "Team Effort",
        "Mythical Defender", "Hardcore Mythical Defender", "True Nobility",
    ],
    "campaign_awards": ["Daredevil", "Mastermind", "A Matter of Perspective"],
    "campaign_diff": [
        "From the Depths", "To the Rooftops", "A Taste of Victory", "Dungeon Crawler",
        "The Belly of the Beast", "The Body of the Beast", "The Crown of the Beast",
        "Dungeon Raider (Campaign)",
        "From Fire with Brimstone", "Through The Crowded Keep", "To the Lofty Summit",
        "Dungeon Defender",
    ],
    "free": [
        "Smithy", "And This Is My Weapon", "To The Limit", "Divine Intention",
        "O Mighty Smiter!", "Obedience Training",
        "Pupil", "Veteran", "Defender of Etheria", "Group Hug", "Master Banker",
        "Catch 'em All",
    ],
    "challenges": [
        "Transcendent Challenge Champion", "Ruthless Defender",
        "Where's The Blueprints?", "Weapon Master", "Friends Forever", "88 Core",
        "Ella, Ella", "Dancing in the Rain", "Wizard Hunter", "You No Take Mushroom",
        "Ogre Block Party", "Speed Freak", "Kobold Exterminator",
        "In A Fowl Mood", "Core Cardio", "Monster Mania", "Monster Madness",
        "Core Destroyer", "Gold Rush", "Gold Blitz",
        "A Challenger Approaches",
    ],
    "survival": [
        "Defense Is the Best Offense",
        "Transcendent Survivalist", "Iron Man", "Tough Guy", "Survivalist", "Thick Skin",
    ],
    "pets": [
        "I've Got Monsters in My Pocket",
        "Dungeon Raider (Assault)", "Mythical Dungeon Raider",
        "Playin' Cupid", "Playin' Mythical Cupid",
    ],
    "shards": [
        "Real Time Strategist", "Mythical Real Time Strategist",
        "Eternia Shard Recovered: Purple", "Nightmare Eternia Shard: Purple",
        "Portal Protector", "Nightmare Portal Protector",
        "Eternia Shard Recovered: Blue", "Nightmare Eternia Shard: Blue",
        "Djinn Recruiter", "Nightmare Djinn Recruiter",
        "Eternia Shard Recovered: Yellow", "Nightmare Eternia Shard: Yellow",
        "Puzzle Solver", "Nightmare Puzzle Solver",
        "Eternia Shard Recovered: Red", "Nightmare Eternia Shard: Red",
        "Boss Crusher", "Nightmare Boss Crusher",
        "Heroes to the Rescue", "Nightmare Heroes to the Rescue",
    ],
    "ultimate_dlc": ["Jingled All the Way"],
    "meta_ud": ["Legendary Defender", "Ultimate Defender"],
    "eternal": [
        "Eternal Defender",
        "Trial by Fire and Lightning", "Nightmare Trial by Fire and Lightning",
        "Out of this World", "Nightmare Out of this World",
        "Hero of Water", "Nightmare Hero of Water",
        "Swashbuckler", "Nightmare Swashbuckler",
        "Crystalline Resurgence", "Nightmare Crystalline Resurgence",
        "Nightmare A Very Misty Christmas", "Nightmare Exterminator",
        "Nightmare Slayer of Omenak", "Nightmare Tomb of Etheria",
        "Nightmare Soothing Dungeoneer", "Nightmare Successful Librarian",
        "Nightmare Pirate Defender", "Coastal Merchant", "Nightmare Coastal Merchant",
        "Nightmare Phoenix Handler", "Nightmare Polybius Invader",
        "Nightmare Egg Escorter", "Nightmare Emerald Explorer", "Nightmare Magus Citizen",
    ],
    "ddt_manual": [
        "Spooky Swashbuckler", "Nightmare Spooky Swashbuckler",
        "Halloween Defender", "Nightmare Halloween Defender",
        "Nature Enthusiast", "Nightmare Nature Enthusiast",
        "Tavern Defender", "Nightmare Tavern Defender",
        "Love Defender", "Nightmare Love Defender",
        "Heart Wanderer", "Nightmare Heart Wanderer",
        "Lifestream Hollow Defender", "Nightmare Lifestream Hollow Defender",
        "Forest Ogre Crusher", "Nightmare Forest Ogre Crusher",
        "Nightmare Jester's Spooktacular Trick-o-Treater",
        "Nightmare Frostdale Christmas Defender",
        "Nightmare Valentine Citadel Lover", "Nightmare Love Machine Worker",
        "Returnia Part 1", "Returnia Part 2", "Returnia Part 3",
        "Returnia Part 4", "Returnia Part 5",
        "Nightmare Workshop Defender", "Nightmare Workshop Dweller",
        "Nightmare Sky Trick O'Treater", "Nightmare Royal Helper",
        "Nightmare Scorched Defender", "Nightmare Boss Rusher",
        "Nightmare Revenge Lover",
    ],
    "ruthless": [],
    "chromatic": ["Chromatic Defender"],
    "extras": [
        "Anniversary Defender", "Nightmare Anniversary Defender",
        "Pumpkin Party", "Pumpkin Party Nightmare",
        "Greater Turkey Hunter", "Nightmare Greater Turkey Hunter",
        "Not So Silent Night", "Nightmare Not So Silent Night",
        "Winter Wonderland", "Nightmare Winter Wonderland",
        "Playin' Anticupid", "Nightmare Playin' Anticupid",
        "Tinkerer's Defender", "Nightmare Tinkerer's Defender",
        "EV Reprogrammer", "Nightmare EV Reprogrammer",
    ],
}

# Flat Chiku sort index (first section wins for duplicates)
_CHIKU_SORT_INDEX: dict[str, int] = {}
_CHIKU_SECTION_FOR: dict[str, str] = {}
_chiku_idx = 0
for _sec_key, _sec_title, _sec_blurb in CHIKU_SECTIONS:
    for _ach_name in CHIKU_SECTION_MEMBERS.get(_sec_key, []):
        if _ach_name not in _CHIKU_SORT_INDEX:
            _CHIKU_SORT_INDEX[_ach_name] = _chiku_idx
            _CHIKU_SECTION_FOR[_ach_name] = _sec_key
            _chiku_idx += 1
_CHIKU_SECTION_LOOKUP = {k: (t, b) for k, t, b in CHIKU_SECTIONS}
_ACH_DEFAULT_INDEX: dict[str, int] = {row[0]: i for i, row in enumerate(ACHIEVEMENTS)}

# Per-achievement Chiku tips / stack hints (shown on each row)
ACH_TIPS: dict[str, str] = {
    "Good Student": "Ranked tutorial or local tutorial toggle — verify in tavern if missing.",
    "Brute Force": "Gunslinger on all 13 campaign maps — hero/pet/ability kills only after wave 1; CC towers OK (EV beam, Ensnare, Gas).",
    "Perfectionist": "Flawless Victory on all 13 campaign maps (≥ Medium) — zero core damage after wave 1.",
    "Daredevil": "Skin of Your Teeth on 6 maps — chip core to ≤100 HP on wave 1, then stay flawless (works on Insane/NM).",
    "Mastermind": "Master Strategist on all 13 campaign maps — tower-only kills; done automatically with Mythical RTS if final wave is tower-only.",
    "Team Effort": "Teamwork award on all 13 maps — use 4 active heroes (F2–F8 emulator counts solo).",
    "Mythical Defender": "Clear all 13 original campaign maps on Nightmare.",
    "Hardcore Mythical Defender": "All 13 campaign maps on Nightmare Hardcore without dying.",
    "True Nobility": "Lord award — kill 50 enemies in 5 seconds (≥ Medium); natural on hero-DPS megastack runs.",
    "A Matter of Perspective": "Defeat Summit boss as P1 with Apprentice, Monk, Huntress, and Squire — 4 runs minimum.",
    "Transcendent Challenge Champion": "All 12 original challenges on Nightmare Hardcore — also unlocks lower challenge tiers.",
    "Transcendent Survivalist": "NM survival wave 25 on all campaign maps + City in the Cliffs — wave 24 clear + lose 25 is enough.",
    "Defense Is the Best Offense": "Pure Strategy wave 10 on all 13 campaign maps + Glitterhelm (≥ Medium) — can stop at wave 9 and lose wave 10.",
    "Mythical Real Time Strategist": "Campaign + Mistymire/Moraggo/Aquanos on NM — minion/Overlord damage only except final wave; no DPS pets.",
    "Real Time Strategist": "Same as Mythical RTS but any difficulty.",
    "I've Got Monsters in My Pocket": "All 31 pet types in item box — overlaps heavily with survival pet farming.",
    "Jingled All the Way": "Etherian Holiday Extravaganza — any difficulty; gas-trap spawns recommended.",
    "Ruthless Defender": "Original campaign + all 13 challenges on Ruthless HC — Chiku recommends deferring until ~6k tower stats.",
    "Chromatic Defender": "Requires Ruthless Defender first, then DDT Lost Quest + challenge maps on NM HC.",
    "No Towers Allowed": "Natural hero-DPS map — stack with Brute Force mindset; run NM HC for Transcendent Challenge Champion.",
}

ACH_STACKS_WITH: dict[str, list[str]] = {
    "Brute Force": [
        "Perfectionist", "Team Effort", "Mythical Defender", "Hardcore Mythical Defender",
        "True Nobility", "From the Depths", "Dungeon Crawler", "Dungeon Defender",
    ],
    "Perfectionist": ["Brute Force", "Team Effort", "Mythical Defender", "Hardcore Mythical Defender", "Daredevil"],
    "Daredevil": ["Perfectionist", "Brute Force"],
    "Team Effort": ["Brute Force", "Perfectionist", "Mythical Defender", "Hardcore Mythical Defender"],
    "Mythical Defender": ["Brute Force", "Perfectionist", "Team Effort", "Hardcore Mythical Defender"],
    "Hardcore Mythical Defender": ["Brute Force", "Perfectionist", "Team Effort", "Mythical Defender"],
    "Mastermind": ["Mythical Real Time Strategist", "Real Time Strategist"],
    "Mythical Real Time Strategist": [
        "Mastermind", "Eternia Shard Recovered: Purple", "Nightmare Eternia Shard: Purple",
        "Eternia Shard Recovered: Blue", "Nightmare Eternia Shard: Blue",
        "Eternia Shard Recovered: Yellow", "Nightmare Eternia Shard: Yellow",
    ],
    "Transcendent Survivalist": ["Survivalist", "Thick Skin", "Tough Guy", "Iron Man"],
    "Transcendent Challenge Champion": [
        "A Challenger Approaches", "Weapon Master", "Kobold Exterminator",
        "Monster Madness", "Dancing in the Rain", "Gold Blitz", "Ogre Block Party",
    ],
}

# Meta sort groups (inner path: Legendary → Ultimate-only → Eternal-only → manual metas)
_LEGENDARY_SET = set(_LEGENDARY_REQS) | {"Legendary Defender"}
_ULTIMATE_ONLY = [n for n in _ULTIMATE_REQS if n not in _LEGENDARY_SET and n != "Legendary Defender"]
_ULTIMATE_ONLY_SET = set(_ULTIMATE_ONLY) | {"Ultimate Defender"}
_ETERNAL_ONLY = [n for n in _ETERNAL_REQS if n not in _ULTIMATE_REQS and n != "Ultimate Defender"]
_ETERNAL_ONLY_SET = set(_ETERNAL_ONLY) | {"Eternal Defender"}

META_SORT_GROUPS: list[tuple[str, str, set[str]]] = [
    ("legendary", "Legendary Defender", _LEGENDARY_SET),
    ("ultimate", "Ultimate Defender (DLC)", _ULTIMATE_ONLY_SET),
    ("eternal", "Eternal Defender (Lost Quests)", _ETERNAL_ONLY_SET),
    ("ruthless", "Ruthless Defender", {"Ruthless Defender"}),
    ("chromatic", "Chromatic Defender", {"Chromatic Defender"}),
    ("other", "Other / Not on Meta Path", set()),
]

_META_GROUP_FOR: dict[str, str] = {}
_META_GROUP_TITLE: dict[str, str] = {}
for _gkey, _gtitle, _gmembers in META_SORT_GROUPS:
    _META_GROUP_TITLE[_gkey] = _gtitle
    for _member in _gmembers:
        _META_GROUP_FOR[_member] = _gkey

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
_WIKI_OVERRIDES: dict[str, str] = {
    "Dungeon Raider (Campaign)":       "Dungeon_Raider",
    "Dungeon Raider (Assault)":        "Dungeon_Raider_(Assault_Mission_Pack)",
    "Nightmare Eternia Shard: Purple": "Nightmare_Eternia_Shard_Recovered:_Purple",
    "Nightmare Eternia Shard: Blue":   "Nightmare_Eternia_Shard_Recovered:_Blue",
    "Nightmare Eternia Shard: Yellow": "Nightmare_Eternia_Shard_Recovered:_Yellow",
    "Nightmare Eternia Shard: Red":    "Nightmare_Eternia_Shard_Recovered:_Red",
    "Winter Wonderland":               "Winter_Wonderland_(Achievement)",
    "Playin' Anticupid":               "Playin%27_Anticupid",
    "Nightmare Playin' Anticupid":     "Nightmare_Playin%27_Anticupid",
    "Playin' Cupid":                   "Playin%27_Cupid",
    "Playin' Mythical Cupid":          "Playin%27_Mythical_Cupid",
    "Tinkerer's Defender":             "Tinkerer%27s_Defender",
    "Nightmare Tinkerer's Defender":   "Nightmare_Tinkerer%27s_Defender",
    "EV Reprogrammer":                 "EV_Reprogrammer",
    "Nightmare EV Reprogrammer":       "Nightmare_EV_Reprogrammer",
    "Nightmare Jester's Spooktacular Trick-o-Treater": "Nightmare_Jester%27s_Spooktacular_Trick-o-Treater",
    "Nightmare Sky Trick O'Treater":   "Nightmare_Sky_Trick_O%27Treater",
    "Crystalline Resurgence":          "Crystalline_Resurgence_(Achievement)",
}

def _wiki_url(name: str) -> str:
    slug = _WIKI_OVERRIDES.get(name)
    if slug is None:
        slug = _url_quote(name.replace(' ', '_'), safe=":!()")
    return _WIKI_BASE + slug

# ── Meta color per achievement ────────────────────────────────────────────────
_ACH_META_COLOR: dict[str, str] = {}
for _m_title, _m_sid, _m_reqs, _m_color in META_DEFS:
    _ACH_META_COLOR[_m_title] = _m_color
    for _req in _m_reqs:
        if _req not in _ACH_META_COLOR:
            _ACH_META_COLOR[_req] = _m_color

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
