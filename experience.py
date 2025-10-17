from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Iterable, Any

try:
    from .utils import clamp, load_attacks_json
except Exception:
    def clamp(lo: float, value: float, hi: float) -> float:
        return lo if value < lo else hi if value > hi else value
    def load_attacks_json() -> dict:
        return {}

try:
    from data_io import load_pokemons as io_load_pokemons
except Exception:
    io_load_pokemons = None


# ------------------------------
# Public configuration & types
# ------------------------------

@dataclass
class XPConfig:
    # Base XP scaling from a defeated Pokémon (rough power proxy)
    base_hp_weight: float = 0.60
    base_def_weight: float = 0.35
    base_spd_weight: float = 0.25
    base_level_weight: float = 6.0      # adds XP proportional to defender level

    # Difficulty multipliers (team size, evolution, level disparity)
    min_team_size_mult: float = 0.75     # ↓ cap if you outnumber the enemy
    max_team_size_mult: float = 1.75     # ↑ cap if enemy outnumbers you
    evo_per_enemy_bonus: float = 0.10    # +10% per “evolved-looking” enemy
    final_stage_bonus: float = 0.05      # +5% per enemy with no future evolution
    level_diff_win_step: float = 0.06    # +6% per average level disadvantage
    level_diff_lose_step: float = 0.04   # -4% per average level advantage
    level_diff_cap: int = 10

    # Participation split
    min_share_on_presence: float = 0.15  # minimum pool share for presence
    last_hit_bonus: float = 0.10         # extra pool weight for last-hitters

    # Global caps to keep numbers sane
    min_total_multiplier: float = 0.25
    max_total_multiplier: float = 2.20

    # Progression / stat growth on level up (only applied if species does NOT evolve at that moment)
    hp_per_level: int = 2
    def_per_level: int = 1
    spdef_per_level: int = 1
    spd_per_level: int = 1

    # XP curves: {"fast", "medium", "slow"}
    default_curve: str = "medium"


# ------------------------------
# Internal helpers
# ------------------------------


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _guess_level(pokemon) -> int:
    lvl = getattr(pokemon, "current_level", None)
    if isinstance(lvl, (int, float)) and lvl >= 0:
        return int(lvl)
    if isinstance(lvl, str) and lvl.strip().isdigit():
        return int(lvl.strip())
    return _safe_int(getattr(pokemon, "level", 1), 1)


def _is_alive(p) -> bool:
    try:
        return bool(p.is_alive())
    except Exception:
        return getattr(p, "health", 0) > 0


def _is_final_stage(pokemon) -> bool:
    return getattr(pokemon, "evolution", None) in (None, "", False)


def _looks_evolved(pokemon) -> bool:
    evo_lvl = getattr(pokemon, "evolution_level", None)
    if evo_lvl is None:
        return False
    cur = _guess_level(pokemon)
    return isinstance(evo_lvl, (int, float)) and cur >= int(evo_lvl)


def _avg_level(team: Iterable) -> float:
    vals = [_guess_level(p) for p in (team or [])]
    return sum(vals) / max(1, len(vals))


def _ensure_progression_fields(pokemon, *, cfg: XPConfig) -> None:
    if not hasattr(pokemon, "level"):
        setattr(pokemon, "level", _guess_level(pokemon) or 1)
    if not hasattr(pokemon, "exp"):
        setattr(pokemon, "exp", _safe_int(getattr(pokemon, "exp", 0), 0))
    if not hasattr(pokemon, "growth_curve"):
        setattr(pokemon, "growth_curve", getattr(pokemon, "growth_curve", cfg.default_curve))


def _xp_required_for(level: int, curve: str) -> int:
    L = max(1, int(level))
    c = (curve or "medium").lower()
    if c == "fast":
        return int(5.0 * (L ** 2) + 30.0 * L)
    if c == "slow":
        return int(10.0 * (L ** 2) + 40.0 * L + 50.0)
    return int(7.5 * (L ** 2) + 35.0 * L + 10.0)


def _xp_needed_to_next(level: int, curve: str) -> int:
    return max(1, _xp_required_for(level + 1, curve) - _xp_required_for(level, curve))


def _base_xp_of(defender, *, cfg: XPConfig) -> int:
    hp = _safe_int(getattr(defender, "maximun_hp", getattr(defender, "max_hp", 0)), 0)
    df = _safe_int(getattr(defender, "defense", 0), 0)
    sd = _safe_int(getattr(defender, "special_defense", 0), 0)
    sp = _safe_int(getattr(defender, "speed", 0), 0)
    lvl = _guess_level(defender)

    score = (
        cfg.base_hp_weight * hp +
        cfg.base_def_weight * (df + sd) / 2.0 +
        cfg.base_spd_weight * sp +
        cfg.base_level_weight * lvl
    )
    return max(5, int(round(score)))


def _team_size_multiplier(my_team_sz: int, enemy_team_sz: int, *, cfg: XPConfig) -> float:
    if my_team_sz <= 0 or enemy_team_sz <= 0:
        return 1.0
    ratio = float(enemy_team_sz) / float(my_team_sz)
    return clamp(cfg.min_team_size_mult, ratio, cfg.max_team_size_mult)


def _evolution_pressure_multiplier(enemy_team: Iterable, *, cfg: XPConfig) -> float:
    enemies = list(enemy_team or [])
    if not enemies:
        return 1.0
    evo_count = sum(1 for p in enemies if _looks_evolved(p))
    final_count = sum(1 for p in enemies if _is_final_stage(p))
    return 1.0 + evo_count * cfg.evo_per_enemy_bonus + final_count * cfg.final_stage_bonus


def _level_disparity_multiplier(my_team: Iterable, enemy_team: Iterable, *, cfg: XPConfig) -> float:
    me = _avg_level(my_team)
    they = _avg_level(enemy_team)
    diff = max(-cfg.level_diff_cap, min(cfg.level_diff_cap, they - me))
    if diff > 0:
        return 1.0 + cfg.level_diff_win_step * diff
    if diff < 0:
        return 1.0 / (1.0 + cfg.level_diff_lose_step * abs(diff))
    return 1.0


def _clamp_mult(x: float, *, cfg: XPConfig) -> float:
    return clamp(cfg.min_total_multiplier, x, cfg.max_total_multiplier)

# -----------------------------
# Species lookup & evolution
# -----------------------------

def _load_species_index() -> Dict[str, Dict[str, Any]]:
    if io_load_pokemons is None:
        return {}
    try:
        return io_load_pokemons() or {}
    except Exception:
        return {}


def _owner_attacks_for(name_display: str) -> Tuple[List[dict], List[dict]]:
    atk = load_attacks_json() or {}
    by_owner = atk.get("by_owner", {}) if isinstance(atk, dict) else {}
    normal = atk.get("normal", []) if isinstance(atk, dict) else []

    # case-insensitive owner lookup
    owner_key = (name_display or "").strip().lower()
    owner_map = {str(k).strip().lower(): v for k, v in by_owner.items()} if isinstance(by_owner, dict) else {}
    specials = list(owner_map.get(owner_key, []) or [])
    normals = list(normal) if isinstance(normal, list) else []
    return specials, normals


def _apply_species(pokemon, species_def: Dict[str, Any], *, keep_level: int, keep_exp: int, clear_buffs: bool = True) -> None:
    # 1) New identity
    display_name = str(species_def.get("name", "") or "").strip() or getattr(pokemon, "name", "")
    new_type = str(species_def.get("element_type", getattr(pokemon, "element_type", "unknown"))).strip().lower()

    # 2) Compute new max HP and preserve ratio
    new_max_hp = int(species_def.get("health", getattr(pokemon, "maximun_hp", 1)))
    new_max_hp = max(1, new_max_hp)
    old_hp = int(getattr(pokemon, "health", 0))
    old_max = int(getattr(pokemon, "maximun_hp", max(1, old_hp)))
    ratio = float(old_hp) / float(old_max) if old_max > 0 else 1.0
    new_hp = max(1, int(round(ratio * new_max_hp)))

    # 3) Attacks for new owner
    specials, normals = _owner_attacks_for(display_name)

    # 4) Assign all new species fields
    pokemon.name = display_name
    pokemon.element_type = new_type
    pokemon.maximun_hp = new_max_hp
    pokemon.max_hp = new_max_hp
    pokemon.health = min(new_hp, new_max_hp)

    pokemon.defense = int(species_def.get("defense", getattr(pokemon, "defense", 0)))
    pokemon.special_defense = int(species_def.get("special_defense", getattr(pokemon, "special_defense", 0)))
    pokemon.speed = int(species_def.get("speed", getattr(pokemon, "speed", 0)))

    # Evol chain for next time
    evo = species_def.get("evolution", None)
    pokemon.evolution = (str(evo).strip().lower() if isinstance(evo, str) and evo.strip() else None)
    evo_lvl = species_def.get("evolution_level", None)
    pokemon.evolution_level = int(evo_lvl) if isinstance(evo_lvl, (int, float)) else None
    # Sync 'current_level' shadow if you use it elsewhere
    pokemon.current_level = keep_level

    # Replace movesets
    pokemon.special_attacks = list(specials)
    pokemon.normal_attacks = list(normals)

    # Keep progression
    setattr(pokemon, "level", keep_level)
    setattr(pokemon, "exp", keep_exp)

    # Clear buffs after species change (optional but recommended)
    if clear_buffs:
        try:
            from .inventory import Inventory  # lazy import to avoid cycles
            Inventory.clear_temp_buffs(pokemon)
        except Exception:
            if hasattr(pokemon, "clear_battle_buffs"):
                pokemon.clear_battle_buffs()
            else:
                try:
                    delattr(pokemon, "_temp_buffs")
                except Exception:
                    setattr(pokemon, "_temp_buffs", {})


def _try_species_lookup(species_key_lc: str) -> Optional[Dict[str, Any]]:
    pokedex = _load_species_index()
    if not pokedex:
        return None
    # direct key
    if species_key_lc in pokedex:
        return pokedex[species_key_lc]
    # fallback: name field equals (case-insensitive)
    for k, v in pokedex.items():
        if str(v.get("name", "")).strip().lower() == species_key_lc:
            return v
    return None

# ---------------------------------
# Battle XP tracking (public API)
# ---------------------------------

@dataclass
class KOEvent:
    attacker: Any
    defender: Any


@dataclass
class Participation:
    turns_on_field: int = 0
    last_hit_kos: int = 0


@dataclass
class BattleXPTracker:
    
    cfg: XPConfig = field(default_factory=XPConfig)
    participants: Dict[Any, Participation] = field(default_factory=dict)
    ko_events: List[KOEvent] = field(default_factory=list)

    # ---------- hooks from combat ----------

    def on_turn_begin(self, active: Iterable[Any]) -> None:
        for p in (active or []):
            self.participants.setdefault(p, Participation()).turns_on_field += 1


    def on_ko(self, attacker: Any, defender: Any) -> None:
        self.ko_events.append(KOEvent(attacker=attacker, defender=defender))
        if attacker is not None:
            self.participants.setdefault(attacker, Participation()).last_hit_kos += 1

    # ---------- difficulty / pool ----------

    def _compute_battle_multiplier(self, winner_team: Iterable, loser_team: Iterable) -> float:
        t_mult = _team_size_multiplier(len(list(winner_team)), len(list(loser_team)), cfg=self.cfg)
        e_mult = _evolution_pressure_multiplier(loser_team, cfg=self.cfg)
        d_mult = _level_disparity_multiplier(winner_team, loser_team, cfg=self.cfg)
        return _clamp_mult(t_mult * e_mult * d_mult, cfg=self.cfg)


    def _compute_xp_pool(self, loser_team: Iterable) -> int:
        total = 0
        for p in (loser_team or []):
            total += _base_xp_of(p, cfg=self.cfg)
        return max(1, total)

    # ---------- split & apply ----------

    def _split_among_participants(self, pool: int, winners: Iterable[Any]) -> List[Tuple[Any, int]]:
        winners = list(winners or [])
        if not self.participants:
            target = winners[0] if winners else None
            return [] if target is None else [(target, pool)]

        presences = {p: pr.turns_on_field for p, pr in self.participants.items() if pr.turns_on_field > 0}
        if not presences:
            target = winners[0] if winners else None
            return [] if target is None else [(target, pool)]

        total_turns = float(sum(presences.values()))
        base_shares: Dict[Any, float] = {}
        for p, turns in presences.items():
            frac = (turns / total_turns) if total_turns > 0 else 0.0
            base_shares[p] = max(self.cfg.min_share_on_presence, frac)

        s = sum(base_shares.values())
        for p in base_shares:
            base_shares[p] = base_shares[p] / s if s > 0 else 0.0

        bonus_weight: Dict[Any, float] = {p: 0.0 for p in base_shares}
        total_kos = sum(pr.last_hit_kos for pr in self.participants.values())
        if total_kos > 0:
            for p, pr in self.participants.items():
                if p in bonus_weight and pr.last_hit_kos > 0:
                    bonus_weight[p] += self.cfg.last_hit_bonus * (pr.last_hit_kos / total_kos)

        final_weight: Dict[Any, float] = {}
        s2 = 0.0
        for p in base_shares:
            w = base_shares[p] + bonus_weight.get(p, 0.0)
            final_weight[p] = w
            s2 += w
        if s2 > 0:
            for p in final_weight:
                final_weight[p] /= s2

        out: List[Tuple[Any, int]] = []
        remaining = pool
        items = list(final_weight.items())
        for i, (p, w) in enumerate(items):
            if i < len(items) - 1:
                share = int(pool * w)
                out.append((p, share))
                remaining -= share
            else:
                out.append((p, max(0, remaining)))
        return [(p, xp) for p, xp in out if xp > 0]

    # ---------- level up & evolution ----------

    def _apply_level_ups_and_evolution(self, pokemon, *, gained: int, lines: List[str]) -> None:
        _ensure_progression_fields(pokemon, cfg=self.cfg)
        curve = getattr(pokemon, "growth_curve", self.cfg.default_curve)
        lvl = int(getattr(pokemon, "level", _guess_level(pokemon)))
        cur_xp = int(getattr(pokemon, "exp", 0))

        # add XP
        new_xp = cur_xp + int(gained)
        setattr(pokemon, "exp", new_xp)

        evolved_now = False
        while True:
            need = _xp_needed_to_next(lvl, curve)
            if new_xp < need:
                break

            # consume for next level
            new_xp -= need
            lvl += 1
            setattr(pokemon, "level", lvl)
            setattr(pokemon, "exp", new_xp)

            # Check if species should evolve at this level
            evo_key = getattr(pokemon, "evolution", None)
            evo_lvl = getattr(pokemon, "evolution_level", None)

            if isinstance(evo_lvl, (int, float)) and evo_key and lvl >= int(evo_lvl):
                # Lookup species entry by lower-cased evolution key
                target_key = str(evo_key).strip().lower()
                species_def = _try_species_lookup(target_key)
                if species_def:
                    old_name = getattr(pokemon, "name", "Pokémon")
                    keep_exp = int(getattr(pokemon, "exp", 0))
                    keep_level = int(getattr(pokemon, "level", lvl))

                    _apply_species(
                        pokemon,
                        species_def,
                        keep_level=keep_level,
                        keep_exp=keep_exp,
                        clear_buffs=True,
                    )
                    evolved_now = True
                    lines.append(f"🌟 {old_name} evolved into {pokemon.name}!")
                    # After species swap, we keep looping in case multiple levels remain.
                    continue
                else:
                    # If evolution target not found, fallback to stat growth
                    lines.append(f"⚠️ Evolution target '{evo_key}' not found in pokedex. Keeping current species.")

            if not evolved_now:
                # Normal stat growth when no evolution this tick
                pokemon.maximun_hp = int(pokemon.maximun_hp + self.cfg.hp_per_level)
                pokemon.health = min(pokemon.health + self.cfg.hp_per_level, pokemon.maximun_hp)
                pokemon.defense = int(pokemon.defense + self.cfg.def_per_level)
                pokemon.special_defense = int(pokemon.special_defense + self.cfg.spdef_per_level)
                pokemon.speed = int(pokemon.speed + self.cfg.spd_per_level)

            lines.append(f"⬆️ {getattr(pokemon, 'name', 'Pokémon')} reached Lv.{lvl}!")

    # ---------- public award ----------

    def finalize_and_award(self, winner_trainer, loser_trainer) -> List[str]:
        lines: List[str] = []
        win_team = getattr(winner_trainer, "team", [])
        lose_team = getattr(loser_trainer, "team", [])

        mult = self._compute_battle_multiplier(win_team, lose_team)
        base_pool = self._compute_xp_pool(lose_team)
        pool = max(1, int(round(mult * base_pool)))

        assignments = self._split_among_participants(pool, winners=win_team)

        for p, xp in assignments:
            _ensure_progression_fields(p, cfg=self.cfg)
            before_lvl = int(getattr(p, "level", _guess_level(p)))
            self._apply_level_ups_and_evolution(p, gained=xp, lines=lines)
            after_lvl = int(getattr(p, "level", before_lvl))
            lines.insert(0, f"🏅 {getattr(p, 'name', 'Pokémon')} gained {xp} XP (Lv.{before_lvl} → Lv.{after_lvl}).")

        t_mult = _team_size_multiplier(len(win_team), len(lose_team), cfg=self.cfg)
        e_mult = _evolution_pressure_multiplier(lose_team, cfg=self.cfg)
        d_mult = _level_disparity_multiplier(win_team, lose_team, cfg=self.cfg)
        lines.append(f"📊 Difficulty multipliers → Team:{t_mult:.2f}  Evolution:{e_mult:.2f}  Level gap:{d_mult:.2f}")

        return lines


class ExperienceManager:
    def __init__(self, config: Optional[XPConfig] = None) -> None:
        self.cfg = config or XPConfig()
        self.tracker: Optional[BattleXPTracker] = None

    def start_battle(self) -> None:
        self.tracker = BattleXPTracker(cfg=self.cfg)

    def on_turn_begin(self, active: Iterable[Any]) -> None:
        if self.tracker:
            self.tracker.on_turn_begin(active)

    def on_ko(self, attacker: Any, defender: Any) -> None:
        if self.tracker:
            self.tracker.on_ko(attacker, defender)

    def finalize(self, winner_trainer, loser_trainer) -> List[str]:
        if not self.tracker:
            self.tracker = BattleXPTracker(cfg=self.cfg)
        lines = self.tracker.finalize_and_award(winner_trainer, loser_trainer)
        self.tracker = None
        return lines