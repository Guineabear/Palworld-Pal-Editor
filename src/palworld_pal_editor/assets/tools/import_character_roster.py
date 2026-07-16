"""Merge current human NPCs and selected experimental Pals into editor data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


WORK_SUITABILITY_MAP = {
    "EmitFlame": "EPalWorkSuitability::EmitFlame",
    "Watering": "EPalWorkSuitability::Watering",
    "Seeding": "EPalWorkSuitability::Seeding",
    "GenerateElectricity": "EPalWorkSuitability::GenerateElectricity",
    "Handcraft": "EPalWorkSuitability::Handcraft",
    "Collection": "EPalWorkSuitability::Collection",
    "Deforest": "EPalWorkSuitability::Deforest",
    "Mining": "EPalWorkSuitability::Mining",
    "ProductMedicine": "EPalWorkSuitability::ProductMedicine",
    "Cool": "EPalWorkSuitability::Cool",
    "Transport": "EPalWorkSuitability::Transport",
    "MonsterFarm": "EPalWorkSuitability::MonsterFarm",
}

ELEMENT_MAP = {"Electricity": "Electric"}

EXPERIMENTAL_HUMAN_PREFIXES = (
    "BOSS_",
    "FireCult_",
    "Hunter_",
    "Ninja",
    "Police_",
    "Quest_",
    "Reward_",
    "Scientist_",
    "SecurityDrone_",
    "Viking_",
    "WildlifeSanctuaryDrone",
)

EXPERIMENTAL_HUMAN_IDS = {
    "Believer_Fat_Cane_Tower",
    "Female_Kunoichi01",
    "Male_Ninja01_Seabase",
    "Male_NinjaElite01_Seabase",
}

EXPERIMENTAL_PAL_IDS = ("BlackFurDragon", "ElecLion")

# These are intentionally not imported. They are aliases, quest duplicates, or
# individual raid components that should not be selectable as complete Pals.
EXCLUDED_PAL_IDS = {
    "AmaterasuWolf_Dark_Quest_Enemy",
    "RAID_YakushimaBoss001_Green_2",
    "RAID_YakushimaBoss002_2",
    "RAID_YakushimaBoss002_Hand_Left",
    "RAID_YakushimaBoss002_Hand_Left_2",
    "RAID_YakushimaBoss002_Hand_Right",
    "RAID_YakushimaBoss002_Hand_Right_2",
    "RAID_YakushimaBoss002_Head",
    "RAID_YakushimaBoss002_Head_2",
    "Sheepball",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def load_localizations(data_root: Path) -> dict[str, dict]:
    locale_paths = {
        "en": "en",
        "zh-CN": "zh-Hans",
        "fr": "fr",
    }
    localizations = {
        editor_locale: read_json(data_root / "l10n" / source_locale / "pals.json")
        for editor_locale, source_locale in locale_paths.items()
    }
    # The reference currently has no Japanese Pal-name file. English is a safe
    # fallback until an authoritative Japanese name becomes available.
    localizations["ja"] = localizations["en"]
    return localizations


def localized_name(localizations: dict[str, dict], locale: str, key: str) -> str:
    return (
        localizations[locale].get(key, {}).get("localized_name")
        or localizations["en"].get(key, {}).get("localized_name")
        or key
    )


def convert_suitabilities(raw: dict) -> dict[str, int]:
    works = raw.get("work_suitability", {})
    return {
        editor_name: works.get(reference_name, 0)
        for reference_name, editor_name in WORK_SUITABILITY_MAP.items()
    }


def convert_stats(raw: dict, melee: int = 100) -> dict[str, int]:
    scaling = raw.get("scaling", {})
    return {
        "HP": scaling.get("hp", 50),
        "ATK": scaling.get("attack", 50),
        "DEF": scaling.get("defense", 50),
        "MELEE": melee,
        "CRAFTSPEED": 100,
        "FOOD": raw.get("max_full_stomach", 100),
    }


def is_experimental_human(key: str) -> bool:
    return key in EXPERIMENTAL_HUMAN_IDS or key.startswith(
        EXPERIMENTAL_HUMAN_PREFIXES
    )


def convert_human(key: str, raw: dict, localizations: dict[str, dict]) -> dict:
    data = {
        "InternalName": key,
        "Elements": [
            ELEMENT_MAP.get(value, value)
            for value in raw.get("element_types", [])
        ],
        "Attacks": {"EPalWazaID::Human_Punch": 1},
        "Human": True,
        "I18n": {
            locale: localized_name(localizations, locale, key)
            for locale in ("en", "zh-CN", "ja", "fr")
        },
        "Stats": convert_stats(raw),
        "SortingKey": {"paldeck": ""},
        "Suitabilities": convert_suitabilities(raw),
        "HasIcon": False,
    }
    if is_experimental_human(key):
        data["Experimental"] = True
    return data


def convert_pal(key: str, raw: dict, localizations: dict[str, dict]) -> dict:
    attacks = {
        f"EPalWazaID::{attack}": level
        for attack, level in raw.get("skill_set", {}).items()
    }
    return {
        "InternalName": key,
        "Elements": [
            ELEMENT_MAP.get(value, value)
            for value in raw.get("element_types", [])
        ],
        "Attacks": attacks,
        "Stats": convert_stats(raw),
        "I18n": {
            locale: localized_name(localizations, locale, key)
            for locale in ("en", "zh-CN", "ja", "fr")
        },
        "SortingKey": {"paldeck": ""},
        "Suitabilities": convert_suitabilities(raw),
        "Experimental": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "data_root", type=Path, help="Reference data/json directory"
    )
    default_data_dir = Path(__file__).resolve().parents[1] / "data"
    parser.add_argument(
        "--human-output",
        type=Path,
        default=default_data_dir / "human_data.json",
    )
    parser.add_argument(
        "--pal-output", type=Path, default=default_data_dir / "pal_data.json"
    )
    args = parser.parse_args()

    reference = read_json(args.data_root / "pals.json")
    localizations = load_localizations(args.data_root)
    humans = read_json(args.human_output)
    pals = read_json(args.pal_output)

    missing_humans = sorted(
        key
        for key, raw in reference.items()
        if raw.get("is_pal") is False and key not in humans
    )
    for key in missing_humans:
        humans[key] = convert_human(key, reference[key], localizations)

    added_pals = []
    for key in EXPERIMENTAL_PAL_IDS:
        if key not in pals:
            pals[key] = convert_pal(key, reference[key], localizations)
            added_pals.append(key)

    accidentally_included = EXCLUDED_PAL_IDS.intersection(pals)
    if accidentally_included:
        raise RuntimeError(
            f"Excluded Pal IDs unexpectedly present: {sorted(accidentally_included)}"
        )

    write_json(args.human_output, humans)
    write_json(args.pal_output, pals)
    experimental_humans = sum(
        bool(humans[key].get("Experimental")) for key in missing_humans
    )
    print(
        f"Added {len(missing_humans)} humans "
        f"({experimental_humans} experimental) and {len(added_pals)} experimental Pals"
    )


if __name__ == "__main__":
    main()
