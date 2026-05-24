from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple, Optional

from .shared import (
    require_type,
    require_keys,
    normalize_string,
    normalize_number,
)
from ..errors import DataValidationError


# Allowed item types and targets
_ALLOWED_ITEM_TYPES: set[str] = {"healing", "revive", "buff", "capture", "evolution", "status_cure"}
_ALLOWED_TARGETS: set[str] = {"ally", "enemy"}

# Effects
_ALLOWED_EFFECT_KINDS: set[str] = {"heal", "revive", "buff", "capture", "evolution", "cure_status"}

# IMPORTANT: include "normal_attacks" because your XAttack uses it.
_ALLOWED_BUFF_STATS: set[str] = {
    "attack",           # por si decides usarlo en futuro
    "defense",
    "special_defense",
    "special_attacks",
    "normal_attacks",   # necesario para XAttack de tu JSON
}


def _canonical_key(s: str) -> str:
    return str(s).strip().lower()


def _require_bool(val: Any, *, where: str) -> bool:
    if isinstance(val, bool):
        return val
    # Permit 0/1 or "true"/"false" rarely, but better fail fast.
    if isinstance(val, (int, float)) and val in (0, 1):
        return bool(val)
    if isinstance(val, str) and val.strip().lower() in {"true", "false"}:
        return val.strip().lower() == "true"
    raise DataValidationError(f"❌ {where}: expected boolean, got {type(val).__name__}({val!r})")


def _validate_heal_effect(effect: dict, *, where: str) -> dict:
    # kind already checked
    amount = effect.get("amount", None)
    percent = effect.get("percent", None)

    if amount is None and percent is None:
        raise DataValidationError(f"❌ {where}: 'heal' effect must include 'amount' or 'percent'")

    out: dict = {"kind": "heal"}

    if amount is not None:
        amt = int(normalize_number(amount, where=f"{where}.amount", min_value=0.0))
        out["amount"] = amt

    if percent is not None:
        per = float(normalize_number(percent, where=f"{where}.percent", min_value=0.0))
        if not (0.0 < per <= 1.0):
            raise DataValidationError(f"❌ {where}.percent must be in (0.0, 1.0], got {per}")
        out["percent"] = per

    # If both are present, keep both; the consumer can decide precedence (I recommend percent > amount)
    return out


def _validate_revive_effect(effect: dict, *, where: str) -> dict:
    revive_hp = normalize_string(effect.get("revive_hp", ""), where=f"{where}.revive_hp", lowercase=True)
    if revive_hp not in {"full", "half"}:
        raise DataValidationError(f"❌ {where}.revive_hp must be 'half' or 'full', got {revive_hp!r}")
    return {"kind": "revive", "revive_hp": revive_hp}


def _validate_buff_effect(effect: dict, *, where: str) -> dict:
    stat = normalize_string(effect.get("stat", ""), where=f"{where}.stat", lowercase=True)
    if stat not in _ALLOWED_BUFF_STATS:
        raise DataValidationError(
            f"❌ {where}.stat must be one of {sorted(_ALLOWED_BUFF_STATS)}, got {stat!r}"
        )
    stages = int(normalize_number(effect.get("stages", 0), where=f"{where}.stages"))
    # stages puede ser negativo (debuff) como en tu ToughHelmet
    return {"kind": "buff", "stat": stat, "stages": stages}


def _validate_capture_effect(effect: dict, *, where: str) -> dict:
    mult = float(normalize_number(effect.get("catch_rate_mult", 1.0), where=f"{where}.catch_rate_mult", min_value=0.1))
    return {"kind": "capture", "catch_rate_mult": mult}


def _validate_evolution_effect(effect: dict, *, where: str) -> dict:
    return {"kind": "evolution"}


def _validate_status_cure_effect(effect: dict, *, where: str) -> dict:
    out: dict = {"kind": "cure_status"}
    status = effect.get("status", None)
    if status is not None:
        s = normalize_string(status, where=f"{where}.status", lowercase=True)
        if s not in {"poison", "paralysis", "sleep"}:
            raise DataValidationError(
                f"❌ {where}.status must be one of 'poison','paralysis','sleep', got {s!r}"
            )
        out["status"] = s
    return out


def _validate_effect(item_type: str, effect: Any, *, where: str) -> dict:
    require_type(effect, dict, where=where)
    kind = normalize_string(effect.get("kind", ""), where=f"{where}.kind", lowercase=True)
    if kind not in _ALLOWED_EFFECT_KINDS:
        raise DataValidationError(f"❌ {where}.kind must be one of {sorted(_ALLOWED_EFFECT_KINDS)}, got {kind!r}")

    if item_type == "healing":
        if kind != "heal":
            raise DataValidationError(f"❌ {where}: healing item must use kind='heal'")
        return _validate_heal_effect(effect, where=where)

    if item_type == "revive":
        if kind != "revive":
            raise DataValidationError(f"❌ {where}: revive item must use kind='revive'")
        return _validate_revive_effect(effect, where=where)

    if item_type == "buff":
        if kind != "buff":
            raise DataValidationError(f"❌ {where}: buff item must use kind='buff'")
        return _validate_buff_effect(effect, where=where)

    if item_type == "capture":
        if kind != "capture":
            raise DataValidationError(f"❌ {where}: capture item must use kind='capture'")
        return _validate_capture_effect(effect, where=where)

    if item_type == "evolution":
        if kind != "evolution":
            raise DataValidationError(f"❌ {where}: evolution item must use kind='evolution'")
        return _validate_evolution_effect(effect, where=where)

    if item_type == "status_cure":
        if kind != "cure_status":
            raise DataValidationError(f"❌ {where}: status_cure item must use kind='cure_status'")
        return _validate_status_cure_effect(effect, where=where)

    # Should not reach here because item_type validated before
    raise DataValidationError(f"❌ {where}: unsupported item type {item_type!r}")


def _validate_one_item(key: str, obj: Any, *, where: str) -> dict:
    require_type(obj, dict, where=where)

    # Required top-level keys
    require_keys(obj, ("name", "type", "target", "effect"), where=where)

    name = normalize_string(obj.get("name"), where=f"{where}.name", lowercase=False)
    item_type = normalize_string(obj.get("type"), where=f"{where}.type", lowercase=True)
    if item_type not in _ALLOWED_ITEM_TYPES:
        raise DataValidationError(
            f"❌ {where}.type must be one of {sorted(_ALLOWED_ITEM_TYPES)}, got {item_type!r}"
        )

    target = normalize_string(obj.get("target"), where=f"{where}.target", lowercase=True)
    if target not in _ALLOWED_TARGETS:
        raise DataValidationError(
            f"❌ {where}.target must be one of {sorted(_ALLOWED_TARGETS)}, got {target!r}"
        )

    effect = _validate_effect(item_type, obj.get("effect"), where=f"{where}.effect")

    # Optional keys
    battle_only = obj.get("battle_only", False)
    reusable = obj.get("reusable", False)
    description = obj.get("description", "")

    battle_only_b = _require_bool(battle_only, where=f"{where}.battle_only") if battle_only is not False else False
    reusable_b = _require_bool(reusable, where=f"{where}.reusable") if reusable is not False else False
    desc_s = str(description) if description is not None else ""

    return {
        "name": name.strip(),
        "type": item_type,         # canonical lower
        "target": target,          # canonical lower
        "effect": effect,          # normalized effect
        "battle_only": battle_only_b,
        "reusable": reusable_b,
        "description": desc_s,
    }


# -------------------- Public API --------------------

def validate_items(raw: Any) -> None:
    require_type(raw, dict, where="items")

    if not raw:
        raise DataValidationError("❌ items: dataset is empty.")

    for key, obj in raw.items():
        where = f"items['{key}']"
        _ = _validate_one_item(key, obj, where=where)


def normalize_items(raw: Any) -> Dict[str, dict]:
    validate_items(raw)

    out: Dict[str, dict] = {}
    for key, obj in raw.items():
        where = f"items['{key}']"
        norm = _validate_one_item(key, obj, where=where)
        out[_canonical_key(key)] = norm
    return out