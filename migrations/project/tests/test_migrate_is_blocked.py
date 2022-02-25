# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.4")
class TestMigrateIsBlocked(UpgradeCase):
    def prepare(self):
        """
        1) Create new Project
        2) Create 6 Tasks:
        Relations:
        - A blocked by B and C
        - B blocked by D and E
        - C blocked by F
        Constraints:
        -C, F, E: is_closed = true
        -A, B, D: is_closed = false
        Expected Result:
        - A, B: is_blocked = true
        - C, D, E, F: is_blocked = false

            Tasks tree
                ----
                  A
                // \\ <-- blocked by
               B    C
             // \\   \\ <-- blocked by
            D    E    F
        """

        def create_task(**values):
            return self.env["project.task"].create(values)

        project = self.env["project.project"].create({"name": "Project 1"})

        folded_stage = self.env["project.task.type"].create(
            {
                "name": "folded stage",
                "fold": True,
            }
        )

        not_folded_stage = self.env["project.task.type"].create(
            {
                "name": "not folded stage",
                "fold": False,
            }
        )

        task_F = create_task(name="Task F", project_id=project.id, stage_id=folded_stage.id)
        task_C = create_task(name="Task C", project_id=project.id, stage_id=folded_stage.id)
        task_C.depend_on_ids |= task_F
        task_E = create_task(name="Task E", project_id=project.id, stage_id=folded_stage.id)
        task_D = create_task(name="Task D", project_id=project.id, stage_id=not_folded_stage.id)
        task_B = create_task(name="Task B", project_id=project.id, stage_id=not_folded_stage.id)
        task_B.depend_on_ids |= task_E | task_D
        task_A = create_task(name="Task A", project_id=project.id, stage_id=not_folded_stage.id)
        task_A.depend_on_ids |= task_B | task_C
        expected_blocked = (task_A.id, task_B.id)
        return (project.id, expected_blocked)

    def check(self, init):
        project_id, blocked_tasks_ids = init
        tasks = self.env["project.task"].search([("project_id", "=", project_id)])
        for task in tasks:
            if task.id in blocked_tasks_ids:
                self.assertTrue(task.is_blocked)
            else:
                self.assertFalse(task.is_blocked)
