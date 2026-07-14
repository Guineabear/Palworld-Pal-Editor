"""Import current passive-skill IDs from a Palworld Save Pal data checkout."""

import argparse
import json
import re
from pathlib import Path


LANGUAGE_DIRS = {"en": "en", "zh-CN": "zh-Hans", "ja": "ja", "fr": "fr"}
BUFF_TYPES = {
    "ShotAttack": "b_Attack",
    "Defense": "b_Defense",
    "CraftSpeed": "b_CraftSpeed",
    "MoveSpeed": "b_MoveSpeed",
}


def clean_text(value):
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path, help="Palworld Save Pal repository root")
    parser.add_argument("--output", type=Path, default=Path("tmp_passive_skills.json"))
    args = parser.parse_args()

    data_root = args.reference / "data" / "json"
    source = json.loads((data_root / "passive_skills.json").read_text(encoding="utf-8"))
    localizations = {}
    for editor_lang, reference_lang in LANGUAGE_DIRS.items():
        path = data_root / "l10n" / reference_lang / "passive_skills.json"
        localizations[editor_lang] = (
            json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        )

    existing_path = Path("../data/pal_passives.json")
    existing = json.loads(existing_path.read_text(encoding="utf-8"))
    converted = {}
    for internal_name, source_skill in source.items():
        old_skill = existing.get(internal_name, {})
        english = localizations["en"].get(internal_name, {})
        english_name = english.get("localized_name") or internal_name
        english_description = clean_text(english.get("description"))
        i18n = {}
        for editor_lang in LANGUAGE_DIRS:
            localized = localizations[editor_lang].get(internal_name, {})
            old_localized = old_skill.get("I18n", {}).get(editor_lang, {})
            i18n[editor_lang] = {
                "Name": localized.get("localized_name") or old_localized.get("Name") or english_name,
                "Description": clean_text(localized.get("description"))
                or old_localized.get("Description")
                or english_description,
            }

        buffs = {
            "b_Attack": 0.0,
            "b_Defense": 0.0,
            "b_CraftSpeed": 0.0,
            "b_MoveSpeed": 0.0,
        }
        for effect in source_skill.get("effects", []):
            buff_name = BUFF_TYPES.get(effect.get("type"))
            if buff_name and effect.get("target") == "ToSelf":
                buffs[buff_name] = float(effect.get("value", 0)) / 100

        converted_skill = {
            "InternalName": internal_name,
            "Rating": source_skill.get("rank", 0),
            "I18n": i18n,
            "Buff": buffs,
        }
        if source_skill.get("disabled"):
            converted_skill["Invalid"] = True
        converted[internal_name] = converted_skill

    for internal_name, old_skill in existing.items():
        converted.setdefault(internal_name, old_skill)

    args.output.write_text(
        json.dumps(converted, indent=4, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(converted)} passive skills to {args.output}")


if __name__ == "__main__":
    main()
