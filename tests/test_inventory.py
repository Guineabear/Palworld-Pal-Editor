import copy
import unittest
from types import SimpleNamespace
from uuid import UUID

from palworld_save_tools.archive import FArchiveWriter
from palworld_save_tools.paltypes import PALWORLD_CUSTOM_PROPERTIES

from palworld_pal_editor.core.item_container_data import (
    InventoryError,
    ItemContainerData,
    ZERO_UUID,
)
from palworld_pal_editor.utils.data_provider import DataProvider


CONTAINER_ID = UUID("11111111-1111-1111-1111-111111111111")


def slot(index, static_id="Wood", count=1, dynamic=False):
    return {
        "RawData": {
            "array_type": "ByteProperty",
            "id": None,
            "value": {
                "slot_index": index,
                "count": count,
                "item": {
                    "static_id": static_id,
                    "dynamic_id": {
                        "created_world_id": UUID("22222222-2222-2222-2222-222222222222") if dynamic else ZERO_UUID,
                        "local_id_in_created_world": UUID("33333333-3333-3333-3333-333333333333") if dynamic else ZERO_UUID,
                    },
                },
                "trailing_bytes": [0] * 20,
            },
            "type": "ArrayProperty",
            "custom_type": ".worldSaveData.ItemContainerSaveData.Value.Slots.Slots.RawData",
        }
    }


def container_value(capacity=3, slots=None):
    return {
        "Slots": {
            "array_type": "StructProperty",
            "id": None,
            "value": {
                "prop_name": "Slots",
                "prop_type": "StructProperty",
                "type_name": "PalItemSlotSaveData",
                "id": ZERO_UUID,
                "values": slots or [],
            },
            "type": "ArrayProperty",
        },
        "SlotNum": {"id": None, "value": capacity, "type": "IntProperty"},
    }


def encoded_property(value):
    writer = FArchiveWriter(custom_properties=PALWORLD_CUSTOM_PROPERTIES)
    writer.u32(0)
    writer.u32(1)
    writer.prop_value(
        "StructProperty",
        "StructProperty",
        {
            "ID": {
                "struct_type": "Guid",
                "struct_id": ZERO_UUID,
                "id": None,
                "value": CONTAINER_ID,
                "type": "StructProperty",
            }
        },
    )
    writer.prop_value("StructProperty", "StructProperty", value)
    return {
        "skip_type": "MapProperty",
        "type": "MapProperty",
        "custom_type": ".worldSaveData.ItemContainerSaveData",
        "key_type": "StructProperty",
        "value_type": "StructProperty",
        "id": None,
        "value": writer.bytes(),
    }


def inventory(capacity=3, slots=None):
    prop = encoded_property(container_value(capacity, slots))
    gvas = SimpleNamespace(properties={"worldSaveData": {"value": {"ItemContainerSaveData": prop}}})
    return ItemContainerData(gvas), prop


class InventoryTests(unittest.TestCase):
    def test_unchanged_lazy_decode_keeps_original_bytes(self):
        data, prop = inventory(slots=[slot(0, count=8)])
        original = prop["value"]
        data.flush()
        self.assertEqual(prop["value"], original)

    def test_add_merges_then_creates_another_stack(self):
        data, _ = inventory(slots=[slot(0, count=8)])
        data.add(CONTAINER_ID, "Wood", 5, 10)
        view = data.describe(CONTAINER_ID)
        self.assertEqual([item["Count"] for item in view["Items"]], [10, 3])
        self.assertFalse(view["Items"][1]["Dynamic"])

    def test_failed_add_is_atomic(self):
        data, _ = inventory(capacity=1, slots=[slot(0, count=8)])
        before = copy.deepcopy(data.describe(CONTAINER_ID))
        with self.assertRaises(InventoryError):
            data.add(CONTAINER_ID, "Wood", 5, 10)
        self.assertEqual(data.describe(CONTAINER_ID), before)

    def test_set_count_and_remove_normal_item(self):
        data, _ = inventory(slots=[slot(0, count=2)])
        data.set_count(CONTAINER_ID, 0, 7, 10)
        self.assertEqual(data.describe(CONTAINER_ID)["Items"][0]["Count"], 7)
        data.remove(CONTAINER_ID, 0)
        self.assertEqual(data.describe(CONTAINER_ID)["Items"], [])

    def test_dynamic_item_is_protected(self):
        data, _ = inventory(slots=[slot(0, "Bat", 1, dynamic=True)])
        with self.assertRaises(InventoryError):
            data.set_count(CONTAINER_ID, 0, 1, 1)
        with self.assertRaises(InventoryError):
            data.remove(CONTAINER_ID, 0)

    def test_flush_can_be_decoded_again(self):
        data, prop = inventory(slots=[slot(0, count=2)])
        data.add(CONTAINER_ID, "Stone", 4, 10)
        data.flush()
        gvas = SimpleNamespace(properties={"worldSaveData": {"value": {"ItemContainerSaveData": prop}}})
        reopened = ItemContainerData(gvas)
        self.assertEqual(
            [(item["StaticId"], item["Count"]) for item in reopened.describe(CONTAINER_ID)["Items"]],
            [("Wood", 2), ("Stone", 4)],
        )


class ItemCatalogueTests(unittest.TestCase):
    def test_palworld_1_0_awakening_materials_are_available(self):
        holy_water = DataProvider.get_item("WorldTreeHolyWater")
        self.assertIsNotNone(holy_water)
        self.assertFalse(holy_water["Dynamic"])
        for element in ("Dark", "Dragon", "Electric", "Fire", "Grass", "Ground", "Ice", "Neutral", "Water"):
            self.assertIsNotNone(DataProvider.get_item(f"PalAwakening_Material_{element}"))

    def test_dynamic_equipment_is_identified(self):
        self.assertTrue(DataProvider.get_item("OldRevolver")["Dynamic"])


if __name__ == "__main__":
    unittest.main()
