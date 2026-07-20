import unittest
from unittest.mock import patch

from palworld_pal_editor.core.pal_entity import PalEntity
from palworld_pal_editor.utils import DataProvider


def bare_pal(parameters=None):
    pal = object.__new__(PalEntity)
    pal._pal_param = parameters or {}
    pal.allow_unsafe_edits = False
    return pal


class PalEntityTestCase(unittest.TestCase):
    def setUp(self):
        self._string_patch = patch.object(PalEntity, "__str__", return_value="test-pal")
        self._string_patch.start()
        self.addCleanup(self._string_patch.stop)


class AwakeningTests(PalEntityTestCase):
    def test_awakening_field_is_created_with_bool_property(self):
        pal = bare_pal()
        pal.IsAwakening = True
        self.assertTrue(pal.IsAwakening)
        self.assertEqual(pal._pal_param["bIsAwakening"]["type"], "BoolProperty")

    def test_awakening_field_can_be_disabled(self):
        pal = bare_pal()
        pal.IsAwakening = True
        pal.IsAwakening = False
        self.assertFalse(pal.IsAwakening)


class PassiveDescriptionTests(unittest.TestCase):
    def test_every_passive_has_an_effective_description(self):
        for passive in DataProvider.get_sorted_passives():
            description, source = DataProvider.get_passive_description(passive["InternalName"])
            self.assertTrue(description.strip())
            self.assertIn(source, {"game", "computed", "unavailable"})


class ActivePresetTests(PalEntityTestCase):
    def test_loadout_updates_learned_and_equipped_arrays_together(self):
        skills = [item["InternalName"] for item in DataProvider.get_sorted_attacks()[:3]]
        pal = bare_pal()
        self.assertTrue(pal.set_ActiveSkillLoadout({"learned": skills, "equipped": skills[:2]}))
        self.assertEqual(pal.MasteredWaza, skills)
        self.assertEqual(pal.EquipWaza, skills[:2])

    def test_loadout_rejects_equipped_skill_that_is_not_learned(self):
        skill = DataProvider.get_sorted_attacks()[0]["InternalName"]
        pal = bare_pal()
        self.assertFalse(pal.set_ActiveSkillLoadout({"learned": [], "equipped": [skill]}))


if __name__ == "__main__":
    unittest.main()
