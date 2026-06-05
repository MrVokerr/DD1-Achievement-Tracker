"""Shared achievement constants (desktop + web export)."""

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

WIKI_OVERRIDES: dict[str, str] = {
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

STACK_HINTS = ACH_STACKS_WITH

_ACH_META_COLOR: dict[str, str] = {}
for _m_title, _m_sid, _m_reqs, _m_color in META_DEFS:
    _ACH_META_COLOR[_m_title] = _m_color
    for _req in _m_reqs:
        if _req not in _ACH_META_COLOR:
            _ACH_META_COLOR[_req] = _m_color

