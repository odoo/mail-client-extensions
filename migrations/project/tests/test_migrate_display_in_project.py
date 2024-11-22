from odoo import Command

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.1")
class TestMigrateDisplayInProject(UpgradeCase):
    def prepare(self):
        project1, project2 = (
            self.env["project.project"]
            .with_context({"mail_create_nolog": True})
            .create(
                [
                    {
                        "name": "Project 1",
                    },
                    {
                        "name": "Project 2",
                    },
                ]
            )
        )
        parent_task = (
            self.env["project.task"]
            .with_context({"mail_create_nolog": True})
            .create(
                {
                    "name": "Parent Task",
                    "project_id": project1.id,
                    "child_ids": [
                        Command.create({"name": "Sub-Task", "project_id": project1.id}),
                        Command.create({"name": "Sub-Task2", "project_id": project1.id, "display_in_project": True}),
                        # display_in_project is True because project is different than the parent task
                        Command.create({"name": "Sub-Task3", "project_id": project2.id}),
                    ],
                }
            )
        )
        return parent_task.id, project1.id, project2.id

    def check(self, init):
        parent_task_id, project1_id, project2_id = init
        parent_task = self.env["project.task"].browse(parent_task_id)
        subtasks = self.env["project.task"].search([("parent_id", "=", parent_task.id)])
        self.assertEqual(len(subtasks), 3, "Parent task should have 3 subtasks")
        subtask3 = subtasks.filtered("display_in_project")
        self.assertEqual(len(subtask3), 1, "Only one subtask should be displayed in project")
        self.assertNotEqual(
            subtask3.project_id,
            parent_task.project_id,
            "The project of the subtask should not be the project 1 as the parent task",
        )
        self.assertEqual(
            subtask3.project_id.id, project2_id, "The project of the subtask should still be the project 2"
        )
        self.assertEqual(
            (subtasks - subtask3).project_id.id,
            project1_id,
            "The project of the other subtasks should still be the project 1",
        )
