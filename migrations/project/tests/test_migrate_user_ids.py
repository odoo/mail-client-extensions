# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.5")
class TestMigrateUserIds(UpgradeCase):
    def prepare(self):
        company = self.env["res.company"].create(
            {
                "name": "Test Company",
            }
        )
        user = self.env["res.users"].create(
            {
                "name": "Mister Project",
                "login": "prj",
            }
        )
        project = (
            self.env["project.project"]
            .with_context(pad_no_create=True)
            .create(
                {
                    "name": "Project 1",
                }
            )
        )
        task = (
            self.env["project.task"]
            .with_context(pad_no_create=True)
            .create(
                {
                    "name": "Task 1",
                    "project_id": project.id,
                    "user_id": user.id,
                }
            )
        )
        return (
            company.id,
            user.id,
            project.id,
            task.id,
        )

    def check(self, init):
        company_id, user_id, project_id, task_id = init
        task = self.env["project.task"].browse(task_id).with_user(user_id)

        self.assertTrue(task.personal_stage_id)
        self.assertTrue(task.personal_stage_type_id)
        stages = self.env["project.task.type"].with_user(user_id).search([("user_id", "=", user_id)])
        self.assertEqual(len(stages), 7)
