import json
import os
import platform
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


SCHEMA_VERSION = 1


def _user_data_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys_platform := os.environ.get("XDG_CONFIG_HOME"):
        base = Path(sys_platform)
    elif platform.system() == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".config"
    return base / "Paldeck"


PRESET_PATH = _user_data_dir() / "passive-presets.json"
ACTIVE_PRESET_PATH = _user_data_dir() / "active-skill-presets.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_document() -> dict:
    return {"schema_version": SCHEMA_VERSION, "presets": []}


def _clean_preset(raw: dict, existing_id: str | None = None) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("Each preset must be an object.")

    name = str(raw.get("name", "")).strip()
    if not name:
        raise ValueError("Preset name cannot be empty.")
    if len(name) > 60:
        raise ValueError("Preset name cannot be longer than 60 characters.")

    skills = raw.get("skills", [])
    if not isinstance(skills, list):
        raise ValueError("Preset skills must be a list.")
    skills = [str(skill).strip() for skill in skills if str(skill).strip()]
    if len(skills) != len(set(skills)):
        raise ValueError("A preset cannot contain duplicate passive skills.")

    now = _now()
    return {
        "id": existing_id or str(raw.get("id") or uuid4()),
        "name": name,
        "skills": skills,
        "created_at": str(raw.get("created_at") or now),
        "updated_at": str(raw.get("updated_at") or now),
    }


def load_document() -> dict:
    if not PRESET_PATH.exists():
        return _empty_document()
    try:
        with PRESET_PATH.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict) or not isinstance(raw.get("presets"), list):
            raise ValueError("Invalid preset document.")
        presets = [_clean_preset(item, str(item.get("id") or uuid4())) for item in raw["presets"]]
        return {"schema_version": SCHEMA_VERSION, "presets": presets}
    except Exception:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        broken = PRESET_PATH.with_name(f"passive-presets.broken-{stamp}.json")
        PRESET_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PRESET_PATH, broken)
        return _empty_document()


def save_document(document: dict) -> dict:
    PRESET_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = PRESET_PATH.with_suffix(".json.tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=2)
    temp_path.replace(PRESET_PATH)
    return document


def create_preset(raw: dict) -> dict:
    document = load_document()
    preset = _clean_preset(raw)
    if any(item["name"].casefold() == preset["name"].casefold() for item in document["presets"]):
        raise ValueError("A preset with that name already exists.")
    document["presets"].append(preset)
    save_document(document)
    return preset


def update_preset(preset_id: str, raw: dict) -> dict:
    document = load_document()
    for index, current in enumerate(document["presets"]):
        if current["id"] != preset_id:
            continue
        merged = {**current, **raw, "updated_at": _now()}
        preset = _clean_preset(merged, preset_id)
        if any(
            item["id"] != preset_id and item["name"].casefold() == preset["name"].casefold()
            for item in document["presets"]
        ):
            raise ValueError("A preset with that name already exists.")
        document["presets"][index] = preset
        save_document(document)
        return preset
    raise KeyError("Preset not found.")


def delete_preset(preset_id: str) -> None:
    document = load_document()
    remaining = [item for item in document["presets"] if item["id"] != preset_id]
    if len(remaining) == len(document["presets"]):
        raise KeyError("Preset not found.")
    document["presets"] = remaining
    save_document(document)


def import_document(raw: dict, replace: bool = False) -> dict:
    if not isinstance(raw, dict) or not isinstance(raw.get("presets"), list):
        raise ValueError("This is not a valid Paldeck passive preset file.")
    incoming = [_clean_preset(item) for item in raw["presets"]]
    names = [item["name"].casefold() for item in incoming]
    if len(names) != len(set(names)):
        raise ValueError("The imported file contains duplicate preset names.")

    document = _empty_document() if replace else load_document()
    by_name = {item["name"].casefold(): item for item in document["presets"]}
    for item in incoming:
        by_name[item["name"].casefold()] = item
    document["presets"] = list(by_name.values())
    return save_document(document)


def _clean_active_preset(raw: dict, existing_id: str | None = None) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("Each preset must be an object.")
    name = str(raw.get("name", "")).strip()
    if not name:
        raise ValueError("Preset name cannot be empty.")
    if len(name) > 60:
        raise ValueError("Preset name cannot be longer than 60 characters.")

    equipped = raw.get("equipped", [])
    learned = raw.get("learned", [])
    if not isinstance(equipped, list) or not isinstance(learned, list):
        raise ValueError("Equipped and learned skills must be lists.")
    equipped = [str(skill).strip() for skill in equipped if str(skill).strip()]
    learned = [str(skill).strip() for skill in learned if str(skill).strip()]
    if len(equipped) > 3:
        raise ValueError("An active preset can equip at most 3 skills.")
    if len(equipped) != len(set(equipped)) or len(learned) != len(set(learned)):
        raise ValueError("An active preset cannot contain duplicate skills.")
    for skill in equipped:
        if skill not in learned:
            learned.append(skill)

    now = _now()
    return {
        "id": existing_id or str(raw.get("id") or uuid4()),
        "name": name,
        "equipped": equipped,
        "learned": learned,
        "created_at": str(raw.get("created_at") or now),
        "updated_at": str(raw.get("updated_at") or now),
    }


def load_active_document() -> dict:
    if not ACTIVE_PRESET_PATH.exists():
        return _empty_document()
    try:
        with ACTIVE_PRESET_PATH.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict) or not isinstance(raw.get("presets"), list):
            raise ValueError("Invalid active preset document.")
        return {
            "schema_version": SCHEMA_VERSION,
            "presets": [_clean_active_preset(item, str(item.get("id") or uuid4())) for item in raw["presets"]],
        }
    except Exception:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        broken = ACTIVE_PRESET_PATH.with_name(f"active-skill-presets.broken-{stamp}.json")
        ACTIVE_PRESET_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ACTIVE_PRESET_PATH, broken)
        return _empty_document()


def save_active_document(document: dict) -> dict:
    ACTIVE_PRESET_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = ACTIVE_PRESET_PATH.with_suffix(".json.tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=2)
    temp_path.replace(ACTIVE_PRESET_PATH)
    return document


def create_active_preset(raw: dict) -> dict:
    document = load_active_document()
    preset = _clean_active_preset(raw)
    if any(item["name"].casefold() == preset["name"].casefold() for item in document["presets"]):
        raise ValueError("A preset with that name already exists.")
    document["presets"].append(preset)
    save_active_document(document)
    return preset


def update_active_preset(preset_id: str, raw: dict) -> dict:
    document = load_active_document()
    for index, current in enumerate(document["presets"]):
        if current["id"] != preset_id:
            continue
        preset = _clean_active_preset({**current, **raw, "updated_at": _now()}, preset_id)
        if any(item["id"] != preset_id and item["name"].casefold() == preset["name"].casefold() for item in document["presets"]):
            raise ValueError("A preset with that name already exists.")
        document["presets"][index] = preset
        save_active_document(document)
        return preset
    raise KeyError("Preset not found.")


def delete_active_preset(preset_id: str) -> None:
    document = load_active_document()
    remaining = [item for item in document["presets"] if item["id"] != preset_id]
    if len(remaining) == len(document["presets"]):
        raise KeyError("Preset not found.")
    document["presets"] = remaining
    save_active_document(document)


def import_active_document(raw: dict, replace: bool = False) -> dict:
    if not isinstance(raw, dict) or not isinstance(raw.get("presets"), list):
        raise ValueError("This is not a valid Paldeck active preset file.")
    incoming = [_clean_active_preset(item) for item in raw["presets"]]
    names = [item["name"].casefold() for item in incoming]
    if len(names) != len(set(names)):
        raise ValueError("The imported file contains duplicate preset names.")
    document = _empty_document() if replace else load_active_document()
    by_name = {item["name"].casefold(): item for item in document["presets"]}
    for item in incoming:
        by_name[item["name"].casefold()] = item
    document["presets"] = list(by_name.values())
    return save_active_document(document)
