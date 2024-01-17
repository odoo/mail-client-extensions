from datetime import datetime

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestMigratePlannedDateEndIntoDateDeadline(UpgradeCase):
    def prepare(self):
        project = self.env["project.project"].create({"name": "Project 1"})
        tasks = self.env["project.task"].create(
            [
                {"name": "Task A", "project_id": project.id, "date_deadline": "2020-01-01"},
                {
                    "name": "Task B",
                    "project_id": project.id,
                    "planned_date_begin": "2020-01-01",
                    "planned_date_end": "2020-01-02",
                },
                {
                    "name": "Task C",
                    "project_id": project.id,
                    "planned_date_begin": "2020-01-01",
                    "date_deadline": "2020-01-02",
                },
                {
                    "name": "Task D",
                    "project_id": project.id,
                    "planned_date_begin": "2020-01-02",
                    "date_deadline": "2020-01-01",
                },
                {"name": "Task E", "project_id": project.id},
                {
                    "name": "Task F",
                    "project_id": project.id,
                    "planned_date_begin": "2020-01-01",
                    "date_deadline": "2020-01-03",
                    "planned_date_end": "2020-01-02",
                },
                {
                    "name": "Task G",
                    "project_id": project.id,
                    "planned_date_begin": "2020-01-01",
                    "date_deadline": "2020-01-02",
                    "planned_date_end": "2020-01-03",
                },
                {
                    "name": "Task H",
                    "project_id": project.id,
                    "planned_date_begin": "2020-01-02",
                    "date_deadline": "2020-01-01",
                    "planned_date_end": "2020-01-03",
                },
            ]
        )

        return tasks.ids

    def check(self, init):
        task_ids = init
        task_A, task_B, task_C, task_D, task_E, task_F, task_G, task_H = self.env["project.task"].browse(task_ids)
        self.assertEqual(task_A.planned_date_begin, False)
        self.assertEqual(task_A.date_deadline, datetime(2020, 1, 1, 0, 0, 0))

        self.assertEqual(task_B.planned_date_begin, datetime(2020, 1, 1, 0, 0, 0))
        self.assertEqual(task_B.date_deadline, datetime(2020, 1, 2, 0, 0, 0))

        self.assertEqual(task_C.planned_date_begin, datetime(2020, 1, 1, 0, 0, 0))
        self.assertEqual(task_C.date_deadline, datetime(2020, 1, 2, 0, 0, 0))

        self.assertEqual(task_D.planned_date_begin, False)
        self.assertEqual(task_D.date_deadline, datetime(2020, 1, 1, 0, 0, 0))

        self.assertEqual(task_E.planned_date_begin, False)
        self.assertEqual(task_E.date_deadline, False)

        self.assertEqual(task_F.planned_date_begin, datetime(2020, 1, 1, 0, 0, 0))
        self.assertEqual(
            task_F.date_deadline, datetime(2020, 1, 2, 0, 0, 0), "It should take the planned_date_end first"
        )

        self.assertEqual(task_G.planned_date_begin, datetime(2020, 1, 1, 0, 0, 0))
        self.assertEqual(
            task_G.date_deadline, datetime(2020, 1, 3, 0, 0, 0), "It should take the planned_date_end first"
        )

        self.assertEqual(task_H.planned_date_begin, datetime(2020, 1, 2, 0, 0, 0))
        self.assertEqual(
            task_H.date_deadline, datetime(2020, 1, 3, 0, 0, 0), "It should take the planned_date_end first"
        )
