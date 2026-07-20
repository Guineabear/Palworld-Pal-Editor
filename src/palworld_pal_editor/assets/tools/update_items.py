"""Build Paldeck's compact item catalogue from extracted Palworld game data.

Usage:
    python update_items.py --source-root path/to/data/json

The source directory must contain items.json and l10n/<locale>/items.json.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


LOCALES = {"en": "en", "fr": "fr", "zh-CN": "zh-Hans"}
TAG_PATTERN = re.compile(r"<[^>]+>")


def clean_text(value: str) -> str:
    return " ".join(TAG_PATTERN.sub(" ", value or "").split())


def build(source_root: Path) -> dict:
    items = json.loads((source_root / "items.json").read_text(encoding="utf-8"))
    localized = {
        target: json.loads(
            (source_root / "l10n" / source / "items.json").read_text(encoding="utf-8")
        )
        for target, source in LOCALES.items()
    }
    result = {}
    for internal_name, item in items.items():
        i18n = {}
        for locale, records in localized.items():
            record = records.get(internal_name, {})
            if record:
                i18n[locale] = {
                    "Name": clean_text(record.get("localized_name", internal_name)),
                    "Description": clean_text(record.get("description", "")),
                }
        result[internal_name] = {
            "Group": item.get("group", "None"),
            "Type": item.get("type_a", "None"),
            "SubType": item.get("type_b", "None"),
            "Rarity": int(item.get("rarity", 0)),
            "MaxStack": int(item.get("max_stack_count", 1)),
            "Weight": item.get("weight", 0),
            "Dynamic": bool(item.get("dynamic")),
            "Disabled": bool(item.get("disabled")),
            "Icon": item.get("icon", ""),
            "SortId": int(item.get("sort_id", 0)),
            "I18n": i18n,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parents[1] / "data" / "item_data.json",
    )
    args = parser.parse_args()
    catalogue = build(args.source_root)
    args.output.write_text(
        json.dumps(catalogue, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Wrote {len(catalogue)} items to {args.output}")


if __name__ == "__main__":
    main()
