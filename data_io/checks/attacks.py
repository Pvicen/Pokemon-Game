from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple
from .shared import (
    require_type,
    require_keys,
    ensure_list_of_dicts,
    normalize_string,
    normalize_number,
)
from ..errors import DataValidationError


# ---- Allowed types: canonical Pokémon types (lower-case) --------------------
# Puedes ajustar o ampliar según tu type_effectiveness.json
_ALLOWED_TYPES: set[str] = {
    "normal", "fire", "water", "grass", "electric", "ice",
    "fighting", "poison", "ground", "flying", "psychic",
    "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"
}

_REQUIRED_ATTACK_KEYS: Tuple[str, ...] = ("name", "type", "damage")


# ---- Internal helpers -------------------------------------------------------

def _canonical_key(name: str) -> str:
    return name.strip().lower()


def _validate_attack_obj(atk: dict, *, where: str) -> dict:
    require_type(atk, dict, where=where)
    require_keys(atk, _REQUIRED_ATTACK_KEYS, where=where)

    # name
    raw_name = normalize_string(atk.get("name"), where=f"{where}.name", lowercase=False)
    # type
    type_norm = normalize_string(atk.get("type"), where=f"{where}.type", lowercase=True)
    if type_norm not in _ALLOWED_TYPES:
        # Si quieres permitir tipos desconocidos sin fallar, cambia a warning/log o quítalo.
        raise DataValidationError(
            f"❌ {where}.type '{type_norm}' is not a recognized type. Allowed: {sorted(_ALLOWED_TYPES)}"
        )
    # damage
    dmg = int(normalize_number(atk.get("damage"), where=f"{where}.damage", min_value=0))

    out = {
        "name": raw_name.strip(),     # conserva capitalización de entrada para UI
        "type": type_norm,           # canónico en minúsculas
        "damage": dmg,
    }

    # optional: accuracy
    if "accuracy" in atk and atk["accuracy"] is not None:
        acc = normalize_number(atk["accuracy"], where=f"{where}.accuracy", min_value=1.0)
        # Límite superior típico 100; si quieres permitir >100, quita este check
        if float(acc) > 100.0:
            raise DataValidationError(f"❌ {where}.accuracy must be in [1..100], got {acc}")
        out["accuracy"] = int(acc)

    # optional: category
    if "category" in atk and atk["category"] is not None:
        cat = normalize_string(atk["category"], where=f"{where}.category", lowercase=True)
        if cat not in {"physical", "special", "status"}:
            raise DataValidationError(
                f"❌ {where}.category must be one of 'physical','special','status', got {cat!r}"
            )
        out["category"] = cat

    return out


def _bucket_attacks(obj: Any, *, where: str) -> List[dict]:
    return ensure_list_of_dicts(obj, where=where)


def _merge_unique_by_name(
    attacks: Iterable[dict],
    *,
    where: str
) -> Dict[str, dict]:
    by_name: Dict[str, dict] = {}
    for i, a in enumerate(attacks, start=1):
        k = _canonical_key(a["name"])
        if k in by_name:
            prev = by_name[k]
            # Collisions: ensure same definition (type/damage/accuracy/category)
            # If not equal, raise error to force data consistency.
            comparable_prev = {kk: prev.get(kk) for kk in ("name", "type", "damage", "accuracy", "category")}
            comparable_new  = {kk: a.get(kk)    for kk in ("name", "type", "damage", "accuracy", "category")}
            if comparable_prev != comparable_new:
                raise DataValidationError(
                    f"❌ {where}: conflicting definitions for attack '{a['name']}'.\n"
                    f"  prev: {comparable_prev}\n"
                    f"  new : {comparable_new}"
                )
            # If equal, silently ignore duplicate
        else:
            by_name[k] = a
    return by_name


# ---- Public validator -------------------------------------------------------

def validate_attacks(raw: Any) -> None:
    require_type(raw, dict, where="attacks")

    # Quickly iterate to validate structure and basic schemas
    for bucket_name, obj in raw.items():
        where_bucket = f"attacks['{bucket_name}']"
        lst = _bucket_attacks(obj, where=where_bucket)
        for idx, atk in enumerate(lst, start=1):
            _ = _validate_attack_obj(atk, where=f"{where_bucket}[{idx}]")

    # Optional: fail if dataset is empty
    if not raw:
        raise DataValidationError("❌ attacks: dataset is empty.")


# ---- Public normalizer ------------------------------------------------------

def normalize_attacks(raw: Any) -> dict:
    validate_attacks(raw)

    # Prepare outputs
    by_owner: Dict[str, List[dict]] = {}
    normal: List[dict] = []

    # First pass: validate & normalize each bucket
    for bucket_name, obj in (raw or {}).items():
        where_bucket = f"attacks['{bucket_name}']"
        lst = _bucket_attacks(obj, where=where_bucket)

        norm_bucket: List[dict] = []
        for idx, atk in enumerate(lst, start=1):
            norm_bucket.append(_validate_attack_obj(atk, where=f"{where_bucket}[{idx}]"))

        # Route to owner vs normal bucket
        key = _canonical_key(bucket_name)
        if key == "normal_attacks" or key == "normal":
            normal.extend(norm_bucket)
        else:
            by_owner.setdefault(key, []).extend(norm_bucket)

    # Deduplicate 'normal' attacks by name
    normal_by_name = _merge_unique_by_name(normal, where="attacks.normal")
    normal = list(normal_by_name.values())

    # Build a global unique map by name across all buckets
    all_attacks: List[dict] = []
    for owner_key, lst in by_owner.items():
        # optional owner-level de-dup within the owner
        by_name_owner = _merge_unique_by_name(lst, where=f"attacks.by_owner['{owner_key}']")
        clean_owner_list = list(by_name_owner.values())
        by_owner[owner_key] = clean_owner_list
        all_attacks.extend(clean_owner_list)

    all_attacks.extend(normal)
    by_name_global = _merge_unique_by_name(all_attacks, where="attacks.all")
    all_attacks = list(by_name_global.values())

    return {
        "by_owner": by_owner,      # owner -> list[attacks]
        "normal": normal,          # list[attacks]
        "by_name": by_name_global, # name(ci) -> attack
        "all": all_attacks,        # list[unique_attacks]
    }