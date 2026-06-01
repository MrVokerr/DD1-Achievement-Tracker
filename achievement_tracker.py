#!/usr/bin/env python3
"""
DD1 Achievement Tracker
=======================
Reads your DunDefHeroes.dun save file and shows which of the 163
Dungeon Defenders achievements you have unlocked.

Usage:
    python achievement_tracker.py

Requirements:
    pip install PySide6

Your .dun file is auto-detected from common Steam library locations.
Use the Browse button to point it at any .dun file (including other
players' saves).
"""
import sys, os, re, struct, json
from urllib.parse import quote as _url_quote

# ── Import parser (same directory) ───────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)

from dun_parser import (
    decompress_dun, BinaryReader,
    parse_options_info, parse_hero_info, parse_equipment,
    MAX_ACHIEVEMENTS, DUN_FILE, DEFAULT_INI,
    get_savefile_beaten_levels,
)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QLineEdit, QScrollArea, QFrame,
    QFileDialog, QSizePolicy, QProgressBar, QButtonGroup,
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QColor, QDesktopServices

# ── Paths ─────────────────────────────────────────────────────────────────────
_DEFAULT_INI = DEFAULT_INI
_MANUAL_JSON = os.path.join(_SCRIPT_DIR, "_ach_manual.json")

# ── Achievement data (name, description, category, steam_id) ─────────────────
# steam_id = None  →  non-Steam achievement (manual checkbox)
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

# ── Manual state helpers ──────────────────────────────────────────────────────

def _load_manual(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_manual(path: str, state: dict) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

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

def load_ach_index(ini_path: str) -> list[str]:
    """Parse UDKEngineSteamworks.ini and return Steam achievement IDs in order."""
    pattern = re.compile(r'AchievementMapping=\(SteamAchievementID="([^"]+)"', re.IGNORECASE)
    result = []
    with open(ini_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = pattern.search(line)
            if m:
                result.append(m.group(1))
    return result


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

# ── Stylesheet ────────────────────────────────────────────────────────────────
STYLESHEET = """
QMainWindow, QWidget#root {
    background: #1e1e1e;
    color: #d4d4d4;
}
QWidget {
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 13px;
}
QLabel#title {
    font-size: 20px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#counter {
    font-size: 14px;
    color: #9cdcfe;
    font-weight: bold;
}
QLabel#status_ok  { color: #4ec94e; font-size: 12px; }
QLabel#status_err { color: #f48771; font-size: 12px; }
QLineEdit#search {
    background: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 6px 10px;
    color: #d4d4d4;
    font-size: 13px;
}
QLineEdit#search:focus { border: 1px solid #007acc; }
QPushButton {
    background: #007acc;
    color: #ffffff;
    border: none;
    border-radius: 5px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: bold;
}
QPushButton:hover   { background: #1a8cdd; }
QPushButton:pressed { background: #005fa3; }
QPushButton#browse_btn { background: #3c3c3c; color: #d4d4d4; }
QPushButton#browse_btn:hover { background: #4f4f4f; }
QScrollArea { border: none; background: #1e1e1e; }
QScrollBar:vertical { background: #2d2d2d; width: 8px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #555; border-radius: 4px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QLabel#section_header {
    font-size: 11px;
    font-weight: bold;
    color: #808080;
    letter-spacing: 1px;
}
QFrame#card      { background: #252526; border: 1px solid #2d2d2d; border-radius: 8px; }
QFrame#card_done { background: #1e2d1e; border: 1px solid #2d4a2d; border-radius: 8px; }
QFrame#meta_card      { background: #252526; border: 1px solid #2d2d2d; border-radius: 8px; }
QFrame#meta_card_done { background: #1e2d1e; border: 1px solid #2d4a2d; border-radius: 8px; }
QProgressBar { background: #3c3c3c; border: none; border-radius: 2px; }
QProgressBar::chunk { background: #007acc; border-radius: 2px; }
QPushButton#filter_btn {
    background: #2d2d2d;
    color: #808080;
    border: 1px solid #3c3c3c;
    border-radius: 5px;
    padding: 5px 14px;
    font-size: 12px;
    font-weight: normal;
}
QPushButton#filter_btn:checked {
    background: #007acc;
    color: #ffffff;
    border-color: #007acc;
    font-weight: bold;
}
QPushButton#filter_btn:hover:!checked { background: #3c3c3c; color: #d4d4d4; }
QCheckBox { background: transparent; color: #d4d4d4; spacing: 5px; }
QCheckBox::indicator {
    width: 15px; height: 15px;
    border: 1px solid #555;
    border-radius: 3px;
    background: #2d2d2d;
}
QCheckBox::indicator:checked  { background: #4ec94e; border-color: #4ec94e; }
QCheckBox::indicator:hover    { border-color: #888; }
"""

# ── Auto-unlock evaluation helpers ───────────────────────────────────────────

def check_ruthless_defender(beaten_levels: dict[str, int]) -> bool:
    """Check if all 13 original campaign maps and challenges are completed on Ruthless Hardcore."""
    if not beaten_levels:
        return False
    campaign_tags = {
        "CAMPDW", "CAMPFF", "CAMPAL", "CAMPMQ", "CAMPSQ", "CAMPCA",
        "CAMPHC", "CAMPTR", "CAMPRG", "CAMPRP", "CAMPES", "CAMPTS", "CAMPGC"
    }
    challenge_tags = {
        "SPECDW", "SPECFF", "WARPP1", "SPECHW", "SPECMQ", "SPECOA",
        "SPECAL", "SPECSQ", "SPECCA", "SPECHC", "SPECTR", "SPECRG", "SPECTH"
    }
    ruthless_hc_bit = 1 << 11  # Bit 11 corresponds to Ruthless Hardcore
    
    campaign_ok = all((beaten_levels.get(tag, 0) & ruthless_hc_bit) != 0 for tag in campaign_tags)
    
    challenges_beaten = sum(
        1 for tag in challenge_tags
        if (beaten_levels.get(tag, 0) & ruthless_hc_bit) != 0
    )
    challenges_ok = challenges_beaten >= 12
    
    return campaign_ok and challenges_ok


def check_chromatic_defender(beaten_levels: dict[str, int]) -> bool:
    """Check if all DDT maps from Spooktacular Bay to Scorched Arabia and Warping Core II to Boss Rush II are completed on Nightmare Hardcore."""
    if not beaten_levels:
        return False
    if not check_ruthless_defender(beaten_levels):
        return False
        
    nm_hc_bit = 1 << 10
    ruthless_hc_bit = 1 << 11
    
    required_tags = {
        "SPECCA", # Spooktacular Bay
        "SPECHW", # Halloween Spooktacular
        "LHOLOC", # Lifestream Hollow
        "VDAY03", # Lover's Paradise
        "RETMIS", # Returnia Mistymire
        "RETMOR", # Returnia Moraggo
        "RETAQU", # Returnia Aquanos
        "RETSKY", # Returnia Sky City
        "RETCRD", # Returnia Crystalline Dimension
        "CDTARA", # Scorched Arabia
        "CDTTWC", # Warping Core II
        "SPECGC", # Boss Rush II
    }
    
    return all(
        ((beaten_levels.get(tag, 0) & nm_hc_bit) != 0 or (beaten_levels.get(tag, 0) & ruthless_hc_bit) != 0)
        for tag in required_tags
    )


# ── Achievement row widget ────────────────────────────────────────────────────

class AchRow(QFrame):
    def __init__(self, name: str, desc: str, category: str, unlocked: bool,
                 is_manual: bool = False, manual_checked: bool = False,
                 dot_color: str = "#3c3c3c", wiki_url: str = "",
                 on_manual_change=None, parent=None, auto_unlocked: bool = False):
        super().__init__(parent)
        self.name = name
        self.desc = desc
        self.category = category
        self.unlocked = unlocked
        self.is_manual = is_manual
        self.manual_checked = manual_checked
        self.auto_unlocked = auto_unlocked
        self._dot_color = dot_color
        self._wiki_url = wiki_url
        self._on_change = on_manual_change
        self._build()

    def _build(self):
        is_done = self.unlocked or (self.is_manual and (self.manual_checked or self.auto_unlocked))
        self.setObjectName("card_done" if is_done else "card")
        self.setFixedHeight(62)
        if self._wiki_url:
            self.setCursor(Qt.PointingHandCursor)
            self.setToolTip("Click to open wiki page")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
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
        dot.setFixedWidth(16)
        dot.setAlignment(Qt.AlignCenter)
        dot.setStyleSheet(
            "color: #4ec94e; font-size: 16px; background: transparent; border: none;" if is_done
            else f"color: {self._dot_color}; font-size: 16px; background: transparent; border: none;"
        )
        layout.addWidget(dot)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        name_color = "#ffffff" if is_done else "#9d9d9d"
        name_lbl = QLabel(self.name)
        name_lbl.setStyleSheet(
            f"color: {name_color}; font-weight: bold; font-size: 13px; "
            "background: transparent; border: none;"
        )
        text_col.addWidget(name_lbl)

        desc_lbl = QLabel(self.desc)
        desc_lbl.setStyleSheet(
            "color: #606060; font-size: 11px; background: transparent; border: none;"
        )
        desc_lbl.setWordWrap(False)
        text_col.addWidget(desc_lbl)

        layout.addLayout(text_col, stretch=1)

        if self.is_manual:
            if self.auto_unlocked:
                badge = QLabel("✓ Save Verified")
                badge.setStyleSheet(
                    "color: #4ec94e; font-size: 11px; font-weight: bold; "
                    "background: transparent; border: none;"
                )
                badge.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                layout.addWidget(badge)
            else:
                cb = QCheckBox()
                cb.setChecked(self.manual_checked)
                cb.setToolTip("Mark as completed")
                cb.toggled.connect(
                    lambda checked, n=self.name: self._on_change and self._on_change(n, checked)
                )
                layout.addWidget(cb)
        else:
            badge_text  = "✓ Unlocked" if self.unlocked else "Locked"
            badge_color = "#4ec94e"    if self.unlocked else "#4a4a4a"
            badge = QLabel(badge_text)
            badge.setStyleSheet(
                f"color: {badge_color}; font-size: 11px; font-weight: bold; "
                "background: transparent; border: none;"
            )
            badge.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(badge)

    def mousePressEvent(self, event):
        if self._wiki_url and event.button() == Qt.LeftButton:
            QDesktopServices.openUrl(QUrl(self._wiki_url))
        super().mousePressEvent(event)


# ── Meta achievement progress card ────────────────────────────────────────────

class MetaCard(QFrame):
    def __init__(self, title: str, color: str, total: int, parent=None):
        super().__init__(parent)
        self._title = title
        self._color = color
        self._total = total
        self.setObjectName("meta_card")
        self.setFixedHeight(76)
        self.setMinimumWidth(145)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        title_lbl = QLabel(title)
        title_lbl.setWordWrap(True)
        title_lbl.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 11px; "
            "background: transparent; border: none;"
        )
        layout.addWidget(title_lbl)

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

        self._lbl = QLabel("Manual" if total == 0 else f"0 / {total}")
        self._lbl.setStyleSheet(
            "color: #808080; font-size: 11px; background: transparent; border: none;"
        )
        layout.addWidget(self._lbl)

    def set_progress(self, done: int, is_complete: bool) -> None:
        if is_complete:
            self.setObjectName("meta_card_done")
            self._lbl.setStyleSheet(
                "color: #4ec94e; font-size: 11px; font-weight: bold; "
                "background: transparent; border: none;"
            )
            if self._bar:
                self._bar.setValue(self._total)
                self._lbl.setText(f"✓ {self._total} / {self._total}")
            else:
                self._lbl.setText("✓ Done")
        else:
            self.setObjectName("meta_card")
            self._lbl.setStyleSheet(
                "color: #808080; font-size: 11px; background: transparent; border: none;"
            )
            if self._bar:
                self._bar.setValue(done)
                self._lbl.setText(f"{done} / {self._total}")
            else:
                self._lbl.setText("Manual")
        self.setStyle(self.style())


# ── Main window ───────────────────────────────────────────────────────────────

class AchievementTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DD1 Achievement Tracker")
        self.resize(920, 760)

        self._dun_path     = DUN_FILE
        self._ini_path     = _DEFAULT_INI
        self._unlocked:    set[str] = set()
        self._manual_state: dict    = _load_manual(_MANUAL_JSON)
        self._filter_mode  = "all"
        self._rows: list[AchRow]    = []
        self._beaten_levels: dict[str, int] = {}

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(8)

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
        self._path_lbl = QLabel(self._dun_path)
        self._path_lbl.setStyleSheet("color: #808080; font-size: 11px;")
        self._path_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_row.addWidget(self._path_lbl)
        browse_btn = QPushButton("Browse…")
        browse_btn.setObjectName("browse_btn")
        browse_btn.clicked.connect(self._browse)
        file_row.addWidget(browse_btn)
        reload_btn = QPushButton("Reload")
        reload_btn.clicked.connect(self._load)
        file_row.addWidget(reload_btn)
        main_layout.addLayout(file_row)

        self._status_lbl = QLabel("")
        self._status_lbl.setObjectName("status_ok")
        main_layout.addWidget(self._status_lbl)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)
        self._meta_cards: list[MetaCard] = []
        for title_m, _sid, reqs, color in META_DEFS:
            card = MetaCard(title_m, color, len(reqs))
            meta_row.addWidget(card)
            self._meta_cards.append(card)
        main_layout.addLayout(meta_row)

        fs_row = QHBoxLayout()
        fs_row.setSpacing(6)
        self._filter_grp = QButtonGroup(self)
        self._filter_grp.setExclusive(True)
        for label, mode in [("All", "all"), ("Unlocked", "unlocked"), ("Missing", "missing")]:
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
        QTimer.singleShot(0, self._load)

    def _load(self):
        self._status_lbl.setObjectName("status_ok")
        import dun_parser
        print("\n--- Diagnostic Info ---", flush=True)
        print(f"Loading save file: {self._dun_path}", flush=True)
        print(f"Using INI file: {self._ini_path}", flush=True)
        print(f"dun_parser module path: {getattr(dun_parser, '__file__', 'unknown')}", flush=True)
        try:
            self._unlocked = get_unlocked_steam_ids(self._dun_path, self._ini_path)
            self._beaten_levels = get_savefile_beaten_levels(self._dun_path)
            self._status_lbl.setText(
                f"Loaded — {len(self._unlocked)} Steam achievements / {len(self._beaten_levels)} level completions verified"
            )
            print(f"Successfully loaded and parsed achievements! Unlocked: {len(self._unlocked)}, Level completions: {len(self._beaten_levels)}", flush=True)
        except Exception as e:
            import traceback
            print(f"\n[ERROR] Failed to load achievements!", file=sys.stderr, flush=True)
            traceback.print_exc()
            self._unlocked = set()
            self._beaten_levels = {}
            self._status_lbl.setObjectName("status_err")
            self._status_lbl.setText(f"Error: {e}")
        self._status_lbl.setStyle(self._status_lbl.style())
        self._update_meta_cards()
        self._rebuild_list()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select DunDefHeroes.dun", os.path.dirname(self._dun_path),
            "DUN Files (*.dun);;All Files (*)"
        )
        if path:
            self._dun_path = path
            self._path_lbl.setText(path)
            self._load()

    def _set_filter(self, mode: str) -> None:
        self._filter_mode = mode
        self._rebuild_list()

    def _on_manual_change(self, name: str, checked: bool) -> None:
        self._manual_state[name] = checked
        _save_manual(_MANUAL_JSON, self._manual_state)
        self._update_meta_cards()
        self._rebuild_list()

    def _update_meta_cards(self) -> None:
        for card, (_title, self_sid, reqs, _color) in zip(self._meta_cards, META_DEFS):
            if not reqs:
                auto_unlocked = False
                if _title == "Ruthless Defender":
                    auto_unlocked = check_ruthless_defender(self._beaten_levels)
                elif _title == "Chromatic Defender":
                    auto_unlocked = check_chromatic_defender(self._beaten_levels)
                is_done = self._manual_state.get(_title, False) or auto_unlocked
                card.set_progress(0, is_done)
            else:
                done = sum(
                    1 for name in reqs
                    if (
                        (_NAME_TO_STEAMID.get(name) in self._unlocked)
                        if _NAME_TO_STEAMID.get(name)
                        else (
                            self._manual_state.get(name, False)
                            or (name == "Ruthless Defender" and check_ruthless_defender(self._beaten_levels))
                            or (name == "Chromatic Defender" and check_chromatic_defender(self._beaten_levels))
                        )
                    )
                )
                manual_override = self._manual_state.get(_title, False)
                if self_sid:
                    is_done = self_sid in self._unlocked
                else:
                    is_done = manual_override or (done >= len(reqs))
                card.set_progress(done, is_done)

    def _rebuild_list(self) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._rows = []
        query = self._search.text().lower().strip()
        current_cat = None

        for name, desc, cat, steam_id in ACHIEVEMENTS:
            is_manual      = (steam_id is None)
            unlocked       = (steam_id in self._unlocked) if steam_id else False
            manual_checked = self._manual_state.get(name, False) if is_manual else False
            
            auto_unlocked = False
            if is_manual:
                if name == "Ruthless Defender":
                    auto_unlocked = check_ruthless_defender(self._beaten_levels)
                elif name == "Chromatic Defender":
                    auto_unlocked = check_chromatic_defender(self._beaten_levels)
            
            is_done        = unlocked or manual_checked or auto_unlocked

            if self._filter_mode == "unlocked" and not is_done:
                continue
            if self._filter_mode == "missing"  and is_done:
                continue

            if query and (
                query not in name.lower()
                and query not in desc.lower()
                and query not in cat.lower()
            ):
                continue

            if cat != current_cat:
                current_cat = cat
                hdr = QLabel(cat.upper())
                hdr.setObjectName("section_header")
                hdr.setContentsMargins(4, 8, 0, 2)
                self._list_layout.insertWidget(self._list_layout.count() - 1, hdr)

            row = AchRow(
                name, desc, cat, unlocked, is_manual, manual_checked,
                dot_color=_ACH_META_COLOR.get(name, "#3c3c3c"),
                wiki_url=_wiki_url(name),
                on_manual_change=self._on_manual_change,
                auto_unlocked=auto_unlocked
            )
            self._list_layout.insertWidget(self._list_layout.count() - 1, row)
            self._rows.append(row)

        steam_total  = sum(1 for *_, sid in ACHIEVEMENTS if sid)
        manual_total = sum(1 for r in ACHIEVEMENTS if not r[3])
        manual_done  = sum(
            1 for r in ACHIEVEMENTS if not r[3] and (
                self._manual_state.get(r[0], False)
                or (r[0] == "Ruthless Defender" and check_ruthless_defender(self._beaten_levels))
                or (r[0] == "Chromatic Defender" and check_chromatic_defender(self._beaten_levels))
            )
        )
        self._counter_lbl.setText(
            f"{len(self._unlocked)} / {steam_total} Steam  ·  {manual_done} / {manual_total} Manual"
        )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = AchievementTracker()
    win.show()
    sys.exit(app.exec())
