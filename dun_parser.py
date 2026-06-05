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

    if VERBOSE:
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
    if VERBOSE:
        print(
            f"Found {len(ordered)} zlib block(s). "
            f"Total decompressed size: {len(result):,} bytes",
            flush=True,
        )
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
    """Parse one EquipmentInfo and return a dict of raw values."""
    e = {}
    e['is_initialized'] = r.read_bool()

    e['damage_reduction_index']      = r.read_arr_i8(MAX_DAMAGEREDUCTIONS)
    # damage_reduction_percentage: i8 × 4, wrapping_sub(127) applied later
    e['damage_reduction_percentage'] = r.read_arr_i8(MAX_DAMAGEREDUCTIONS)

    # stat_modifiers: i32 × 11, wrapping_sub(127) applied later
    e['stat_modifiers']              = r.read_arr_i32(MAX_LEVELUP_STATS)
    # spawn_stat_modifiers: i32 × 11 (NOT transformed)
    e['spawn_stat_modifiers']        = r.read_arr_i32(MAX_LEVELUP_STATS)

    e['weapon_damage_bonus']         = r.read_i32()
    # i8 fields that need wrapping_sub(127):
    e['weapon_number_of_projectiles_bonus'] = r.read_i8()
    e['weapon_speed_of_projectiles_bonus']  = r.read_i32()
    e['weapon_additional_damage_type_index'] = r.read_i8()
    e['weapon_additional_damage_amount']     = r.read_i32()
    e['weapon_draw_scale_multiplier']        = r.read_f32()
    e['weapon_swing_speed_multiplier']       = r.read_f32()
    e['level']                               = r.read_i32()
    e['stored_mana']                         = r.read_i32()
    e['spawn_quality']                       = r.read_f32()
    e['spawn_randomizer_multiplier']         = r.read_f32()
    e['weapon_blocking_bonus']               = r.read_i8()
    e['weapon_alt_damage_bonus']             = r.read_i32()
    e['weapon_clip_ammo_bonus']              = r.read_i32()
    e['weapon_reload_speed_bonus']           = r.read_i8()
    e['weapon_knockback_bonus']              = r.read_i8()
    e['weapon_charge_speed_bonus']           = r.read_i8()
    e['weapon_shots_per_second_bonus']       = r.read_i8()

    e['name_index_base']               = r.read_i8()
    e['name_index_damage_reduction']   = r.read_i8()
    e['name_index_quality_descriptor'] = r.read_i8()
    e['primary_color_set']             = r.read_i8()
    e['secondary_color_set']           = r.read_i8()
    e['equipment_id_1']                = r.read_i32()
    e['equipment_id_2']                = r.read_i32()
    e['minimum_sell_worth']            = r.read_i32()
    e['maximum_sell_worth']            = r.read_i32()
    e['max_equipment_level']           = r.read_i32()
    e['dropped_location_x']            = r.read_i32()
    e['dropped_location_y']            = r.read_i32()
    e['dropped_location_z']            = r.read_i32()

    e['can_be_upgraded']             = r.read_i8()
    e['allow_renaming_at_max_upgrade'] = r.read_i8()
    e['cant_be_dropped']             = r.read_i8()
    e['cant_be_sold']                = r.read_i8()
    e['auto_lock_in_item_box']       = r.read_i8()
    e['did_onetime_effect']          = r.read_i8()
    e['is_locked']                   = r.read_i8()
    e['manual_lr']                   = r.read_i8()

    e['primary_color_override']   = r.read_linear_color()
    e['secondary_color_override'] = r.read_linear_color()

    e['user_equipment_name'] = r.read_string()
    e['user_forger_name']    = r.read_string()
    e['description']         = r.read_string()
    e['equipment_template']  = r.read_string()
    e['equipment_timestamp'] = r.read_string()

    e['folder_id']    = r.read_i32()
    e['is_secondary'] = r.read_bool()

    e['stat_equipment_ids']   = r.read_arr_i32(MAX_BUFF_SLOTS)
    e['stat_equipment_tiers'] = r.read_arr_i32(MAX_BUFF_SLOTS)

    e['quality_beam_color_override'] = r.read_linear_color()
    e['equipment_feature_string']    = r.read_string()

    e['hide_quality_descriptors'] = r.read_i8()
    e['equipment_feature_byte1']  = r.read_i8()
    e['equipment_feature_byte2']  = r.read_i8()
    e['feature_array'] = r.read_arr_i32(MAX_FEATURE_SLOTS)

    return e


def get_savefile_beaten_levels(dun_path: str) -> dict[str, int]:
    """Parse DunDefHeroes.dun and return a dict of beaten level tags -> difficulty mask."""
    try:
        if not os.path.exists(dun_path):
            return {}
        data = decompress_dun(dun_path)
        r = BinaryReader(data)
        r.read_i32()  # version
        r.read_i32()  # size
        parse_options_info(r)
        hero_count = r.read_i32()
        for _ in range(hero_count):
            parse_hero_info(r)
            eq_count = r.read_i32()
            for _ in range(eq_count):
                parse_equipment(r)
        
        # Read achievement bytes
        r.read(MAX_ACHIEVEMENTS)
        
        # Parse CoreUnlockInfo [i8; 40]
        r.read(40)
        
        # Parse CrystalCoreOptions
        r.read_i32()  # core_index
        r.read_linear_color()
        r.read_linear_color()
        r.read_linear_color()
        
        # Parse beaten_levels: Vec<LevelProgressInfo>
        beaten_count = r.read_i32()
        beaten_map = {}
        for _ in range(beaten_count):
            tag = r.read_string()
            diff_mask = r.read_i32()
            if tag:
                beaten_map[tag.upper()] = diff_mask
        return beaten_map
    except Exception as e:
        print(f"[Error parsing beaten levels]: {e}")
        return {}

