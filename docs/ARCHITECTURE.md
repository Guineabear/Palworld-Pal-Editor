# Paldeck architecture

## Runtime

The Python package owns save parsing, the in-memory model, validation, backups, and the local HTTP API. The Vue application is a local client served by that process. No save data is uploaded by Paldeck.

## Code map

- `src/palworld_pal_editor/core/save_manager.py`: world lifecycle and save round trips.
- `src/palworld_pal_editor/core/pal_entity.py`: typed Pal fields and editing rules.
- `src/palworld_pal_editor/core/player_entity.py`: player and technology fields.
- `src/palworld_pal_editor/core/item_container_data.py`: lazy item-container decoding, validated stack edits, and map re-encoding.
- `src/palworld_pal_editor/api/`: authenticated local API routes.
- `src/palworld_pal_editor/assets/data/`: extracted Palworld data and localization.
- `frontend/palworld-pal-editor-webui/src/stores/paleditor.js`: client state and API operations.
- `frontend/palworld-pal-editor-webui/src/components/`: editor surfaces.
- `frontend/palworld-pal-editor-webui/src/assets/tokens.css`: locked Paldeck design tokens.

## Compatibility rules

Unknown save fields must be preserved. New fields should use the exact Unreal property type used by the game. Safe mode validates ordinary game limits; Advanced editing may preserve experimental combinations but must never silently enable itself or leak between requests.

Preset files live in the user configuration location rather than beside the executable, allowing application upgrades without deleting them.

`ItemContainerSaveData` remains byte-preserved during the initial world load. It is decoded only when Inventory is opened, then re-encoded before saving if an item changed. This keeps ordinary Pal editing fast on large dedicated servers. Dynamic equipment records remain untouched; the interface exposes them read-only until Paldeck can create the matching `DynamicItemSaveData` record with confidence.

The generated `item_data.json` catalogue contains extracted Palworld item metadata and localization. Maintainers can rebuild it with `assets/tools/update_items.py` from an extracted `data/json` directory rather than hand-editing the generated file.

## Release checklist

Run unit tests, Python compilation, dependency checks, the Vue production build, and a copied-save write/reopen test. Build artifacts are produced by `.github/workflows/release-build.yml` from version tags.
