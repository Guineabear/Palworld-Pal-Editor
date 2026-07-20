"""Lazy, save-safe access to Palworld item containers.

ItemContainerSaveData is deliberately skipped during the initial world load.  Large
servers can contain tens of thousands of containers, so decoding it eagerly more
than doubles the memory cost for users who only want to edit Pals.  This module
decodes the preserved map on first inventory access and writes it back before the
world is saved.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from uuid import UUID

from palworld_save_tools.archive import FArchiveReader, FArchiveWriter
from palworld_save_tools.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS


ITEM_CONTAINER_PATH = ".worldSaveData.ItemContainerSaveData"
ZERO_UUID = UUID(int=0)


class InventoryError(ValueError):
    """Raised when an inventory edit would create an unsafe save record."""


@dataclass(frozen=True)
class ItemSlotView:
    slot_index: int
    static_id: str
    count: int
    dynamic: bool


class ItemContainerData:
    """Decode and mutate the skipped ItemContainerSaveData map on demand."""

    def __init__(self, gvas_file):
        world = gvas_file.properties["worldSaveData"]["value"]
        self._property = world["ItemContainerSaveData"]
        if self._property.get("skip_type") != "MapProperty":
            raise InventoryError("Item container data is not available in the expected format")

        self._entries = self._decode_entries()
        self._by_id = {str(self._key_id(entry["key"])): entry for entry in self._entries}
        self._slot_template = self._find_slot_template()
        self._dirty = False

    def _decode_entries(self) -> list[dict]:
        reader = FArchiveReader(
            self._property["value"],
            PALWORLD_TYPE_HINTS,
            PALWORLD_CUSTOM_PROPERTIES,
        )
        reader.u32()
        count = reader.u32()
        key_type = self._property["key_type"]
        value_type = self._property["value_type"]
        key_struct_type = "StructProperty"
        value_struct_type = "StructProperty"
        entries = []
        for _ in range(count):
            entries.append(
                {
                    "key": reader.prop_value(
                        key_type, key_struct_type, f"{ITEM_CONTAINER_PATH}.Key"
                    ),
                    "value": reader.prop_value(
                        value_type, value_struct_type, f"{ITEM_CONTAINER_PATH}.Value"
                    ),
                }
            )
        if not reader.eof():
            raise InventoryError("Unexpected trailing item-container data")
        return entries

    @staticmethod
    def _key_id(key: dict) -> UUID:
        return key["ID"]["value"]

    @staticmethod
    def _slots(entry: dict) -> list[dict]:
        try:
            return entry["value"]["Slots"]["value"]["values"]
        except (KeyError, TypeError):
            return []

    @staticmethod
    def _capacity(entry: dict) -> int:
        try:
            return int(entry["value"]["SlotNum"]["value"])
        except (KeyError, TypeError, ValueError):
            return 0

    @staticmethod
    def _raw(slot: dict) -> dict:
        return slot["RawData"]["value"]

    def _find_slot_template(self) -> dict | None:
        for entry in self._entries:
            slots = self._slots(entry)
            if slots:
                return copy.deepcopy(slots[0])
        return None

    def _entry(self, container_id: UUID | str) -> dict:
        entry = self._by_id.get(str(container_id))
        if entry is None:
            raise InventoryError(f"Inventory container {container_id} was not found")
        return entry

    @staticmethod
    def is_dynamic(raw: dict) -> bool:
        dynamic_id = raw.get("item", {}).get("dynamic_id", {})
        return any(
            dynamic_id.get(key) not in (None, ZERO_UUID)
            for key in ("created_world_id", "local_id_in_created_world")
        )

    def describe(self, container_id: UUID | str) -> dict:
        entry = self._entry(container_id)
        items = []
        for slot in sorted(self._slots(entry), key=lambda value: self._raw(value)["slot_index"]):
            raw = self._raw(slot)
            items.append(
                {
                    "SlotIndex": int(raw["slot_index"]),
                    "StaticId": raw["item"]["static_id"],
                    "Count": int(raw["count"]),
                    "Dynamic": self.is_dynamic(raw),
                }
            )
        return {"ContainerId": str(container_id), "Capacity": self._capacity(entry), "Items": items}

    def add(self, container_id: UUID | str, static_id: str, count: int, max_stack: int) -> None:
        if not static_id or count < 1:
            raise InventoryError("Choose an item and enter a quantity of at least 1")
        if max_stack < 1:
            raise InventoryError("This item cannot be created as a normal inventory stack")

        entry = self._entry(container_id)
        slots = self._slots(entry)
        stack_space = sum(
            max_stack - self._raw(slot)["count"]
            for slot in slots
            if self._raw(slot)["item"]["static_id"] == static_id
            and not self.is_dynamic(self._raw(slot))
            and self._raw(slot)["count"] < max_stack
        )
        free_slot_count = max(0, self._capacity(entry) - len(slots))
        if count > stack_space + free_slot_count * max_stack:
            raise InventoryError("There are not enough free slots for that quantity")

        remaining = count
        for slot in slots:
            raw = self._raw(slot)
            if (
                raw["item"]["static_id"] == static_id
                and not self.is_dynamic(raw)
                and raw["count"] < max_stack
            ):
                amount = min(remaining, max_stack - raw["count"])
                raw["count"] += amount
                remaining -= amount
                if remaining == 0:
                    self._dirty = True
                    return

        used = {self._raw(slot)["slot_index"] for slot in slots}
        free = [index for index in range(self._capacity(entry)) if index not in used]
        needed = (remaining + max_stack - 1) // max_stack
        if self._slot_template is None:
            raise InventoryError("No compatible item-slot template exists in this save")

        for slot_index in free[:needed]:
            amount = min(remaining, max_stack)
            slot = copy.deepcopy(self._slot_template)
            raw = self._raw(slot)
            raw.update(
                {
                    "slot_index": slot_index,
                    "count": amount,
                    "item": {
                        "static_id": static_id,
                        "dynamic_id": {
                            "created_world_id": ZERO_UUID,
                            "local_id_in_created_world": ZERO_UUID,
                        },
                    },
                }
            )
            slots.append(slot)
            remaining -= amount
        self._dirty = True

    def set_count(self, container_id: UUID | str, slot_index: int, count: int, max_stack: int) -> None:
        entry = self._entry(container_id)
        slot = self._find_slot(entry, slot_index)
        raw = self._raw(slot)
        if self.is_dynamic(raw):
            raise InventoryError("Linked equipment records are protected from direct editing")
        if count < 1 or count > max_stack:
            raise InventoryError(f"Quantity must be between 1 and {max_stack}")
        raw["count"] = count
        self._dirty = True

    def remove(self, container_id: UUID | str, slot_index: int) -> None:
        entry = self._entry(container_id)
        slot = self._find_slot(entry, slot_index)
        if self.is_dynamic(self._raw(slot)):
            raise InventoryError("Linked equipment records are protected from direct removal")
        self._slots(entry).remove(slot)
        self._dirty = True

    def _find_slot(self, entry: dict, slot_index: int) -> dict:
        for slot in self._slots(entry):
            if self._raw(slot)["slot_index"] == slot_index:
                return slot
        raise InventoryError(f"Inventory slot {slot_index} was not found")

    def flush(self) -> None:
        if not self._dirty:
            return
        writer = FArchiveWriter(custom_properties=PALWORLD_CUSTOM_PROPERTIES)
        writer.u32(0)
        writer.u32(len(self._entries))
        key_type = self._property["key_type"]
        value_type = self._property["value_type"]
        key_struct_type = "StructProperty"
        value_struct_type = "StructProperty"
        for entry in self._entries:
            writer.prop_value(key_type, key_struct_type, entry["key"])
            writer.prop_value(value_type, value_struct_type, entry["value"])
        self._property["value"] = writer.bytes()
        self._dirty = False
