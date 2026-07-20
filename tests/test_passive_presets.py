import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from palworld_pal_editor import passive_presets
from palworld_pal_editor.core.pal_entity import PalEntity


class PassivePresetTests(unittest.TestCase):
    def test_more_than_six_presets_with_more_than_six_skills_survive_reload(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            preset_path = Path(temp_dir) / "passive-presets.json"
            with patch.object(passive_presets, "PRESET_PATH", preset_path):
                for index in range(8):
                    passive_presets.create_preset(
                        {
                            "name": f"Advanced preset {index}",
                            "skills": [f"Skill_{index}_{skill}" for skill in range(8)],
                        }
                    )

                document = passive_presets.load_document()

        self.assertEqual(8, len(document["presets"]))
        self.assertTrue(all(len(preset["skills"]) == 8 for preset in document["presets"]))

    def test_import_accepts_more_than_six_presets_and_skills(self):
        incoming = {
            "schema_version": 1,
            "presets": [
                {
                    "name": f"Imported {index}",
                    "skills": [f"ImportedSkill_{index}_{skill}" for skill in range(7)],
                }
                for index in range(7)
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            preset_path = Path(temp_dir) / "passive-presets.json"
            with patch.object(passive_presets, "PRESET_PATH", preset_path):
                document = passive_presets.import_document(incoming)
                reloaded = passive_presets.load_document()

        self.assertEqual(7, len(document["presets"]))
        self.assertEqual(document, reloaded)

    def test_more_than_six_skills_requires_advanced_editing_to_apply(self):
        pal = PalEntity.__new__(PalEntity)
        pal._pal_param = {}
        skills = [f"Skill_{index}" for index in range(7)]
        setter = PalEntity.set_PassiveSkillList.__wrapped__

        with patch(
            "palworld_pal_editor.core.pal_entity.DataProvider.has_passive_skill",
            return_value=True,
        ):
            pal.allow_unsafe_edits = False
            self.assertFalse(setter(pal, skills))
            pal.allow_unsafe_edits = True
            self.assertTrue(setter(pal, skills))

        self.assertEqual(skills, pal.PassiveSkillList)


if __name__ == "__main__":
    unittest.main()
