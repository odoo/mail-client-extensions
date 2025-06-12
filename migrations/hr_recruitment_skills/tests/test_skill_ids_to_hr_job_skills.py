from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestSkillIdsToHrJobSkill(UpgradeCase):
    def prepare(self):
        no_default_level_skill_type, default_level_skill_type = self.env["hr.skill.type"].create(
            [
                {"name": "No Default Level Skill Type"},
                {"name": "Default Level Skill Type"},
            ],
        )

        (
            no_default_level_1,
            _no_default_level_2,
            _no_default_level_3,
            _default_level_1,
            default_level_2,
            _default_level_3,
        ) = self.env["hr.skill.level"].create(
            [
                {
                    "default_level": False,
                    "level_progress": 0,
                    "name": "No Default Level 1",
                    "skill_type_id": no_default_level_skill_type.id,
                },
                {
                    "default_level": False,
                    "level_progress": 50,
                    "name": "No Default Level 2",
                    "skill_type_id": no_default_level_skill_type.id,
                },
                {
                    "default_level": False,
                    "level_progress": 100,
                    "name": "No Default Level 3",
                    "skill_type_id": no_default_level_skill_type.id,
                },
                {
                    "default_level": False,
                    "level_progress": 0,
                    "name": "Default Level 1",
                    "skill_type_id": default_level_skill_type.id,
                },
                {
                    "default_level": True,
                    "level_progress": 50,
                    "name": "Default Level 2",
                    "skill_type_id": default_level_skill_type.id,
                },
                {
                    "default_level": False,
                    "level_progress": 100,
                    "name": "Default Level 3",
                    "skill_type_id": default_level_skill_type.id,
                },
            ],
        )

        no_default_level_skill, default_level_skill = self.env["hr.skill"].create(
            [
                {"name": "No Default Level Skill", "skill_type_id": no_default_level_skill_type.id},
                {"name": "Default Level Skill", "skill_type_id": default_level_skill_type.id},
            ],
        )

        job_1, job_2, job_3, job_4 = self.env["hr.job"].create(
            [
                {
                    "name": "Job With No Default Level Skill",
                    "skill_ids": [no_default_level_skill.id],
                },
                {
                    "name": "Job With Default Level Skill",
                    "skill_ids": [default_level_skill.id],
                },
                {
                    "name": "Job With Both Skills",
                    "skill_ids": [no_default_level_skill.id, default_level_skill.id],
                },
                {
                    "name": "Another Job With Default Level Skill",
                    "skill_ids": [default_level_skill.id],
                },
            ],
        )

        return {
            "job_ids": [job_1.id, job_2.id, job_3.id, job_4.id],
            "no_default_level_skill_type": no_default_level_skill_type.id,
            "default_level_skill_type": default_level_skill_type.id,
            "expected_no_default_level": no_default_level_1.id,
            "expected_default_level": default_level_2.id,
        }

    def check(self, init):
        job_1, job_2, job_3, job_4 = self.env["hr.job"].browse(init["job_ids"])

        self.assertTrue(job_1.job_skill_ids, "Job 1 should have a job skill")
        self.assertEqual(len(job_1.job_skill_ids), 1, "Job 1 should have exactly one job skill")
        self.assertEqual(
            job_1.job_skill_ids.skill_type_id.id,
            init["no_default_level_skill_type"],
            "The job skill on Job 1 should be of the type 'No Default Level Skill Type'",
        )
        self.assertEqual(
            job_1.job_skill_ids.skill_level_id.id,
            init["expected_no_default_level"],
            "The job skill on Job 1 should have the level 'No Default Level 1'",
        )

        self.assertTrue(job_2.job_skill_ids, "Job 2 should have a job skill")
        self.assertEqual(len(job_2.job_skill_ids), 1, "Job 1 should have exactly one job skill")
        self.assertEqual(
            job_2.job_skill_ids.skill_type_id.id,
            init["default_level_skill_type"],
            "The job skill on Job 2 should be of the type 'Default Level Skill Type'",
        )
        self.assertEqual(
            job_2.job_skill_ids.skill_level_id.id,
            init["expected_default_level"],
            "The job skill on Job 2 should have the level 'Default Level 2'",
        )

        self.assertTrue(job_3.job_skill_ids, "Job 3 should have a job skill")
        self.assertEqual(len(job_3.job_skill_ids), 2, "Job 3 should have exactly two job skills")
        self.assertCountEqual(
            job_3.job_skill_ids.skill_type_id.ids,
            [init["no_default_level_skill_type"], init["default_level_skill_type"]],
            "The job skills on Job 3 should be of the type 'No Default Level Skill Type' and 'Default Level Skill Type'",
        )
        self.assertCountEqual(
            job_3.job_skill_ids.skill_level_id.ids,
            [init["expected_no_default_level"], init["expected_default_level"]],
            "The job skills on Job 3 should have the level 'No Default Level 1' and 'Default Level 2'",
        )

        self.assertTrue(job_4.job_skill_ids, "Job 4 should have a job skill")
        self.assertEqual(len(job_4.job_skill_ids), 1, "Job 4 should have exactly one job skills")
        self.assertEqual(
            job_4.job_skill_ids.skill_type_id.id,
            init["default_level_skill_type"],
            "The job skill on Job 4 should be of the type 'Default Level Skill Type'",
        )
        self.assertEqual(
            job_4.job_skill_ids.skill_level_id.id,
            init["expected_default_level"],
            "The job skill on Job 4 should have the level 'Default Level 2'",
        )
        self.assertNotEqual(
            job_2.job_skill_ids,
            job_4.job_skill_ids,
            "Job 2 and Job 4 should not have the same skill record even though the composition of their skills is the same",
        )
