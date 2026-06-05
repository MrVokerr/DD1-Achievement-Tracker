"""Launch DD1 Achievement Tracker with pythonw — no console window on Windows.

Browse selects DunDefHeroes.dun on first run; UI settings are stored locally in
_ach_manual.json (gitignored — may contain absolute paths).
"""
import achievement_tracker

if __name__ == "__main__":
    achievement_tracker.main()
