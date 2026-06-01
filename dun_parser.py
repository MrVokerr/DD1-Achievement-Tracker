"""
dun_parser.py  —  Minimal DD1 save-file parser for achievement tracking.

Reads and decompresses DunDefHeroes.dun, then skips through the binary
structure to reach the achievement byte array.  Only the functions
needed by achievement_tracker.py are included.

Based on the save-file format documented at:
  https://github.com/tbolb/dd_savefile_reader
"""
import struct, zlib, os, sys

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_ACHIEVEMENTS    = 500
MAX_TUTORIAL_SETS   = 10
MAX_DAMAGEREDUCTIONS = 4
MAX_LEVELUP_STATS   = 11
MAX_BUFF_SLOTS      = 10
MAX_FEATURE_SLOTS   = 10

VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv

# ── Auto-detect paths ─────────────────────────────────────────────────────────
_DUN_FILENAME = "DunDefHeroes.dun"
_INI_FILENAME = "UDKEngineSteamworks.ini"

# Common Steam library roots to search (tries every drive A-G and common paths)
_STEAM_ROOTS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Dungeon Defenders",
    r"C:\Program Files\Steam\steamapps\common\Dungeon Defenders",
    r"D:\Steam\steamapps\common\Dungeon Defenders",
    r"D:\SteamLibrary\steamapps\common\Dungeon Defenders",
    r"E:\Steam\steamapps\common\Dungeon Defenders",
    r"E:\SteamLibrary\steamapps\common\Dungeon Defenders",
    r"F:\Games\steamapps\common\Dungeon Defenders",
    r"F:\Steam\steamapps\common\Dungeon Defenders",
    r"F:\SteamLibrary\steamapps\common\Dungeon Defenders",
    r"G:\Steam\steamapps\common\Dungeon Defenders",
    r"G:\SteamLibrary\steamapps\common\Dungeon Defenders",
]

def _find_dun() -> str:
    candidates = []
    for root in _STEAM_ROOTS:
        for sub in ("Win32", "Win64"):
            p = os.path.join(root, "Binaries", sub, _DUN_FILENAME)
            if os.path.exists(p):
                candidates.append(p)
    if candidates:
        return max(candidates, key=os.path.getmtime)
    # Return a plausible placeholder so the UI can display it
    return os.path.join(_STEAM_ROOTS[0], "Binaries", "Win32", _DUN_FILENAME)

def _find_ini() -> str:
    for root in _STEAM_ROOTS:
        p = os.path.join(root, "UDKGame", "Config", _INI_FILENAME)
        if os.path.exists(p):
            return p
    return os.path.join(_STEAM_ROOTS[0], "UDKGame", "Config", _INI_FILENAME)

DUN_FILE    = _find_dun()
DEFAULT_INI = _find_ini()

# ── BinaryReader ──────────────────────────────────────────────────────────────

class BinaryReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos  = 0

    def remaining(self) -> int:
        return len(self.data) - self.pos

    def read(self, n: int) -> bytes:
        if self.pos + n > len(self.data):
            raise EOFError(
                f"Tried to read {n} bytes at pos {self.pos} but only "
                f"{len(self.data) - self.pos} remain"
            )
        chunk = self.data[self.pos : self.pos + n]
        self.pos += n
        return chunk

    def read_bool(self) -> bool:
        return self.read(1)[0] != 0

    def read_i8(self) -> int:
        return struct.unpack_from('<b', self.read(1))[0]

    def read_u8(self) -> int:
        return self.read(1)[0]

    def read_i32(self) -> int:
        return struct.unpack_from('<i', self.read(4))[0]

    def read_f32(self) -> float:
        return struct.unpack_from('<f', self.read(4))[0]

    def read_string(self):
        """
        Option<String>:
          0       → None
          < 0     → UTF-16 LE, |size|*2 bytes (null-terminated)
          > 0     → CP-1252,   size bytes (null-terminated)
        """
        size = self.read_i32()
        if size == 0:
            return None
        if size < 0:
            raw  = self.read(abs(size) * 2)
            text = raw.decode('utf-16-le', errors='replace').rstrip('\x00')
        else:
            raw  = self.read(size)
            text = raw.rstrip(b'\x00').decode('cp1252', errors='replace')
        return text if text.strip() else None

    def read_arr_i8(self, n: int) -> list:
        return [self.read_i8()  for _ in range(n)]

    def read_arr_i32(self, n: int) -> list:
        return [self.read_i32() for _ in range(n)]

    def read_vec_i8(self) -> list:
        return [self.read_i8()  for _ in range(self.read_i32())]

    def read_vec_i32(self) -> list:
        return [self.read_i32() for _ in range(self.read_i32())]

    def read_linear_color(self) -> tuple:
        return (self.read_f32(), self.read_f32(), self.read_f32(), self.read_f32())

    def log(self, label: str):
        if VERBOSE:
            print(f"  [0x{self.pos:08X}] {label}", flush=True)

# ── Decompressor ──────────────────────────────────────────────────────────────

_ZLIB_MAGIC = [b'\x78\x9c', b'\x78\x01', b'\x78\xda', b'\x78\x5e']

def decompress_dun(path: str) -> bytes:
    """Find all zlib blocks in the raw .dun file, decompress, and concatenate."""
    with open(path, 'rb') as fh:
        raw = fh.read()

    print(f"Raw file size: {len(raw):,} bytes", flush=True)

    blocks = []
    for magic in _ZLIB_MAGIC:
        start = 0
        while True:
            idx = raw.find(magic, start)
            if idx == -1:
                break
            try:
                data = zlib.decompress(raw[idx:])
                blocks.append((idx, data))
            except zlib.error:
                pass
            start = idx + 1

    if not blocks:
        raise RuntimeError("No valid zlib blocks found in the .dun file!")

    seen, ordered = set(), []
    for off, data in sorted(blocks, key=lambda x: x[0]):
        if off not in seen:
            seen.add(off)
            ordered.append(data)

    result = b''.join(ordered)
    print(f"Found {len(ordered)} zlib block(s). Total decompressed size: {len(result):,} bytes", flush=True)
    return result

# ── Structure parsers (skip-only — advance the cursor to reach ach bytes) ─────

def parse_options_info(r: BinaryReader):
    """Consume the OptionsInfo block."""
    # OptionsFixedStruct
    r.read_bool(); r.read_bool(); r.read_bool(); r.read_bool(); r.read_bool()
    r.read_arr_i32(MAX_TUTORIAL_SETS)
    r.read_f32(); r.read_f32(); r.read_f32(); r.read_f32()
    r.read_bool(); r.read_bool(); r.read_bool()
    r.read_f32(); r.read_f32(); r.read_f32()
    r.read_bool(); r.read_bool(); r.read_bool(); r.read_bool(); r.read_bool()
    r.read_bool()
    r.read_i8(); r.read_i8()
    r.read_bool(); r.read_bool()
    r.read_f32(); r.read_f32(); r.read_f32()
    r.read_i32()
    r.read_bool(); r.read_bool()
    r.read_i8()
    r.read_f32()
    r.read_i8(); r.read_i32(); r.read_bool()
    r.read_vec_i8()
    r.read_vec_i32()
    r.read_vec_i32()
    # Strings
    r.read_string(); r.read_string(); r.read_string(); r.read_string()
    # SearchFilterSettings
    r.read_vec_i32(); r.read_vec_i32()
    r.read_i8(); r.read_i8(); r.read_i8(); r.read_i8()
    r.read_i8(); r.read_i8(); r.read_i8(); r.read_i8(); r.read_i8()
    r.read_vec_i32()


def parse_hero_info(r: BinaryReader) -> tuple:
    """Consume a HeroInfo block. Returns (name, template, eq_count, {})."""
    r.read_bool()
    r.read_arr_i32(10)
    r.read_i32(); r.read_i32(); r.read_i32()
    r.read_i32(); r.read_i32(); r.read_i32(); r.read_i32()
    r.read_i32()
    r.read_linear_color(); r.read_linear_color(); r.read_linear_color()
    r.read_i8(); r.read_i8(); r.read_i8()
    hero_name     = r.read_string()
    hero_template = r.read_string()
    for _ in range(10):
        r.read_string()
    equipment_count = r.read_i32()
    return (hero_name, hero_template, equipment_count, {})


def parse_equipment(r: BinaryReader) -> dict:
    """Consume one EquipmentInfo block."""
    r.read_bool()
    r.read_arr_i8(MAX_DAMAGEREDUCTIONS)
    r.read_arr_i8(MAX_DAMAGEREDUCTIONS)
    r.read_arr_i32(MAX_LEVELUP_STATS)
    r.read_arr_i32(MAX_LEVELUP_STATS)
    r.read_i32()
    r.read_i8(); r.read_i32(); r.read_i8(); r.read_i32()
    r.read_f32(); r.read_f32()
    r.read_i32(); r.read_i32(); r.read_f32(); r.read_f32()
    r.read_i8(); r.read_i32(); r.read_i32()
    r.read_i8(); r.read_i8(); r.read_i8(); r.read_i8()
    r.read_i8(); r.read_i8(); r.read_i8(); r.read_i8()
    r.read_i8(); r.read_i8(); r.read_i8()
    r.read_i8(); r.read_i8()
    r.read_i32(); r.read_i32(); r.read_i32(); r.read_i32()
    r.read_i32(); r.read_i32(); r.read_i32(); r.read_i32()
    r.read_i8(); r.read_i8(); r.read_i8(); r.read_i8()
    r.read_i8(); r.read_i8(); r.read_i8(); r.read_i8()
    r.read_linear_color(); r.read_linear_color()
    r.read_string(); r.read_string(); r.read_string()
    r.read_string(); r.read_string()
    r.read_i32()
    r.read_bool()
    r.read_arr_i32(MAX_BUFF_SLOTS)
    r.read_arr_i32(MAX_BUFF_SLOTS)
    r.read_linear_color()
    r.read_string()
    r.read_i8(); r.read_i8(); r.read_i8()
    r.read_arr_i32(MAX_FEATURE_SLOTS)
    return {}
