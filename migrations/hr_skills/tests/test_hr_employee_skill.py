from freezegun import freeze_time

from odoo import fields
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

from odoo.tests import Form


@change_version("saas~18.4")
class TestAccrualLevel(UpgradeCase):

    def _create_skill_types(self, vals_list):
        skill_types = self.env["hr.skill.type"]
        for vals in vals_list:
            with Form(self.env["hr.skill.type"]) as skill_type_form:
                skill_type_form.name = vals["name"]
                for skill_val in vals["skills"]:
                    with skill_type_form.skill_ids.new() as skill:
                        skill.name = skill_val["name"]
                for level_val in vals["levels"]:
                    with skill_type_form.skill_level_ids.new() as level:
                        level.name = level_val["name"]
                        level.level_progress = level_val["level_progress"]
            skill_types += skill_type_form.save()
        return skill_types

    def prepare(self):
        employee1, employee2 = self.env["hr.employee"].create(
            [
                {"name": "Test Employee 1"},
                {"name": "Test Employee 2"},
            ]
        )

        language = self._create_skill_types(
            [
                {
                    "name": "Languages",
                    "skills": [
                        {"name": "Arabic"},
                        {"name": "English"},
                        {"name": "French"},
                    ],
                    "levels": [
                        {"name": "A1", "level_progress": 10},
                        {"name": "A2", "level_progress": 30},
                        {"name": "B1", "level_progress": 50},
                        {"name": "B2", "level_progress": 70},
                        {"name": "C1", "level_progress": 90},
                        {"name": "C2", "level_progress": 100},
                    ],
                },
            ]
        )
        with freeze_time("2025-01-01"):
            emp1_arabic_a1, emp1_english_a1, emp2_english_a1 = self.env["hr.employee.skill"].create(
                [
                    {
                        "employee_id": employee1.id,
                        "skill_id": language.skill_ids[0].id,
                        "skill_level_id": language.skill_level_ids[5].id,
                        "skill_type_id": language.id,
                    },
                    {
                        "employee_id": employee1.id,
                        "skill_id": language.skill_ids[1].id,
                        "skill_level_id": language.skill_level_ids[5].id,
                        "skill_type_id": language.id,
                    },
                    {
                        "employee_id": employee2.id,
                        "skill_id": language.skill_ids[1].id,
                        "skill_level_id": language.skill_level_ids[5].id,
                        "skill_type_id": language.id,
                    },
                ]
            )

        with freeze_time("2025-02-01"):
            (emp1_arabic_a1 + emp2_english_a1).write({"skill_level_id": language.skill_level_ids[4].id})

        with freeze_time("2025-03-01"):
            emp1_english_a1.write({"skill_level_id": language.skill_level_ids[4].id})
            self.env["hr.employee.skill"].create(
                [
                    {
                        "employee_id": employee2.id,
                        "skill_id": language.skill_ids[2].id,
                        "skill_level_id": language.skill_level_ids[4].id,
                        "skill_type_id": language.id,
                    }
                ]
            )

        return employee1.id, employee2.id

    def check(self, init):
        employee1_id, employee2_id = init
        employee1, employee2 = self.env["hr.employee"].browse([employee1_id, employee2_id])

        employee1_employee_skills = employee1.employee_skill_ids
        employee1_current_employee_skills = employee1.current_employee_skill_ids
        self.assertEqual(len(employee1_employee_skills.ids), 4)
        self.assertEqual(len(employee1_current_employee_skills.ids), 2)

        names_array = employee1_employee_skills.mapped("display_name")
        expected_display_names = ["English: A1", "English: A2", "Arabic: A1", "Arabic: A2"]
        self.assertCountEqual(names_array, expected_display_names)

        names_array = employee1_current_employee_skills.mapped("display_name")
        expected_display_names = ["English: A2", "Arabic: A2"]
        self.assertCountEqual(names_array, expected_display_names)

        emp1_arabic_a1, emp1_arabic_a2, emp1_english_a1, emp1_english_a2 = employee1_employee_skills.sorted(
            "display_name"
        )
        self.assertEqual(emp1_arabic_a1.valid_from, fields.Date.from_string("2025-01-01"))
        self.assertEqual(emp1_arabic_a1.valid_to, fields.Date.from_string("2025-01-31"))
        self.assertEqual(emp1_arabic_a2.valid_from, fields.Date.from_string("2025-02-01"))
        self.assertFalse(emp1_arabic_a2.valid_to)
        self.assertEqual(emp1_english_a1.valid_from, fields.Date.from_string("2025-01-01"))
        self.assertEqual(emp1_english_a1.valid_to, fields.Date.from_string("2025-02-28"))
        self.assertEqual(emp1_english_a2.valid_from, fields.Date.from_string("2025-03-01"))
        self.assertFalse(emp1_english_a2.valid_to)

        employee2_employee_skills = employee2.employee_skill_ids
        employee2_current_employee_skills = employee2.current_employee_skill_ids
        self.assertEqual(len(employee2_employee_skills.ids), 3)
        self.assertEqual(len(employee2_current_employee_skills.ids), 2)

        names_array = employee2_employee_skills.mapped("display_name")
        expected_display_names = ["English: A1", "English: A2", "French: A2"]
        self.assertCountEqual(names_array, expected_display_names)

        names_array = employee2_current_employee_skills.mapped("display_name")
        expected_display_names = ["English: A2", "French: A2"]
        self.assertCountEqual(names_array, expected_display_names)

        emp2_english_a1, emp2_english_a2, emp2_french_a2 = employee2_employee_skills.sorted("display_name")
        self.assertEqual(emp2_english_a1.valid_from, fields.Date.from_string("2025-01-01"))
        self.assertEqual(emp2_english_a1.valid_to, fields.Date.from_string("2025-01-31"))
        self.assertEqual(emp2_english_a2.valid_from, fields.Date.from_string("2025-02-01"))
        self.assertFalse(emp2_english_a2.valid_to)
        self.assertEqual(emp2_french_a2.valid_from, fields.Date.from_string("2025-03-01"))
        self.assertFalse(emp2_french_a2.valid_to)

