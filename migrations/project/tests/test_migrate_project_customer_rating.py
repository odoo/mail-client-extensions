from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestMigrateProjectCustomerRating(UpgradeCase):
    def prepare(self):
        self.env["res.config.settings"].create(
            {
                "group_project_recurring_tasks": True,
                "group_project_rating": True,
            }
        ).execute()
        projects = project_1, project_2, project_3, project_4, project_5, project_6, project_7 = self.env[
            "project.project"
        ].create(
            [
                {
                    "name": "Test Project 1",
                    "rating_active": True,
                    "rating_status": "periodic",
                    "rating_status_period": "yearly",
                },
                {
                    "name": "Test Project 2",
                    "rating_active": True,
                    "rating_status": "periodic",
                    "rating_status_period": "weekly",
                },
                {
                    "name": "Test Project 3",
                    "rating_active": True,
                    "rating_status": "stage",
                },
                {
                    "name": "Test Project 4",
                    "rating_active": True,
                    "rating_status": "stage",
                },
                {
                    "name": "Test Project 5",
                    "rating_active": False,
                },
                {
                    "name": "Test Project 6",
                    "rating_active": True,
                    "rating_status": "periodic",
                    "rating_status_period": "weekly",
                },
                {
                    "name": "Test Project 7",
                    "rating_active": False,
                },
            ]
        )
        mail_template = self.env["mail.template"].create({"name": "Test Rating Template"})
        stages = stage_1, stage_2, stage_3, _stage_4 = self.env["project.task.type"].create(
            [
                {
                    "name": "Test Stage 1",
                    "sequence": 1,
                    "project_ids": [(6, 0, projects.ids)],
                    "rating_template_id": mail_template.id,
                },
                {
                    "name": "Test Stage 2",
                    "sequence": 2,
                    "project_ids": [(6, 0, (project_5 + project_7).ids)],
                    "rating_template_id": mail_template.id,
                },
                {
                    "name": "Test Stage 3",
                    "sequence": 3,
                    "project_ids": [(6, 0, project_1.ids)],
                    "rating_template_id": mail_template.id,
                },
                {
                    "name": "Test Stage 4",
                    "sequence": 4,
                    "project_ids": [(6, 0, project_1.ids)],
                },
            ]
        )
        tasks = self.env["project.task"].create(
            [
                {
                    "name": "Test Task 1",
                    "project_id": project_1.id,
                    "stage_id": stage_3.id,
                },
                {
                    "name": "Test Task 2",
                    "project_id": project_2.id,
                    "stage_id": stage_1.id,
                    "recurring_task": True,
                },
                {
                    "name": "Test Task 3",
                    "project_id": project_3.id,
                    "stage_id": stage_1.id,
                },
                {
                    "name": "Test Task 4",
                    "project_id": project_4.id,
                    "stage_id": stage_1.id,
                },
                {
                    "name": "Test Task 5",
                    "project_id": project_5.id,
                    "stage_id": stage_1.id,
                },
                {
                    "name": "Test Task 6",
                    "project_id": project_6.id,
                    "stage_id": stage_1.id,
                },
                {
                    "name": "Test Task 7",
                    "project_id": project_7.id,
                    "stage_id": stage_2.id,
                },
            ]
        )
        return (
            projects.ids,
            stages.ids,
            tasks.ids,
        )

    def check(self, init):
        project_ids, stage_ids, task_ids = init
        projects = project_1, project_2, project_3, project_4, project_5, project_6, project_7 = self.env[
            "project.project"
        ].browse(project_ids)
        _stage_1, stage_2, stage_3, stage_4 = self.env["project.task.type"].browse(stage_ids)
        task_1, task_2, task_3, task_4, task_5, task_6, task_7 = self.env["project.task"].browse(task_ids)

        self.assertEqual(len(project_1.type_ids), 3, "Three stages should be linked to `project_1`.")
        self.assertEqual(
            project_1.type_ids[0].rating_active, True, "This new stage should be configured with `project_1` settings."
        )
        self.assertEqual(
            project_1.type_ids[0].rating_status,
            "periodic",
            "This new stage should be configured with `project_1` settings.",
        )
        self.assertEqual(
            project_1.type_ids[0].rating_status_period,
            "yearly",
            "This new stage should be configured with `project_1` settings.",
        )
        self.assertEqual(
            project_1.type_ids[1],
            stage_3,
            "`stage_3` should have been kept for `project_1` as it's this stage is only linked to this project.",
        )
        self.assertEqual(stage_3.rating_active, True, "`stage_3` should be configured with `project_1` settings.")
        self.assertEqual(stage_3.rating_status, "periodic", "`stage_3` should be configured with `project_1` settings.")
        self.assertEqual(
            stage_3.rating_status_period, "yearly", "`stage_3` should be configured with `project_1` settings."
        )

        self.assertEqual(len(project_2.type_ids), 1, "Only one stage should have been generated.")
        self.assertEqual(
            project_2.type_ids.rating_active, True, "This new stage should be configured with `project_2` settings."
        )
        self.assertEqual(
            project_2.type_ids.rating_status,
            "periodic",
            "This new stage should be configured with `project_2` settings.",
        )
        self.assertEqual(
            project_2.type_ids.rating_status_period,
            "weekly",
            "This new stage should be configured with `project_2` settings.",
        )
        self.assertEqual(
            project_2.type_ids,
            project_6.type_ids,
            "`project_2` and `project_6` should share the same stage as they have the same settings.",
        )

        self.assertEqual(len(project_3.type_ids), 1, "Only one stage should have been generated.")
        self.assertEqual(
            project_3.type_ids.rating_active, True, "This new stage should be configured with `project_3` settings."
        )
        self.assertEqual(
            project_3.type_ids.rating_status, "stage", "This new stage should be configured with `project_3` settings."
        )
        self.assertEqual(
            project_3.type_ids.rating_status_period,
            "monthly",
            "This new stage should be configured with `project_3` settings.",
        )
        self.assertEqual(
            project_3.type_ids,
            project_4.type_ids,
            "`project_3` and `project_4` should share the same stage as they have the same settings.",
        )

        self.assertEqual(len(project_5.type_ids), 2, "Two stages should be linked to `project_5`.")
        self.assertFalse(
            project_5.type_ids[0].rating_active,
            "This new stage should be configured with `project_5` settings (default settings values).",
        )
        self.assertEqual(
            project_5.type_ids[0].rating_status,
            "stage",
            "This new stage should be configured with `project_5` settings (default settings values).",
        )
        self.assertEqual(
            project_5.type_ids[0].rating_status_period,
            "monthly",
            "This new stage should be configured with `project_5` settings (default settings values).",
        )
        self.assertEqual(
            project_5.type_ids,
            project_7.type_ids,
            "`project_5` and `project_7` should share the same stages as they have the same settings.",
        )
        self.assertEqual(
            project_5.type_ids[1],
            stage_2,
            "`stage_2` should have been kept for `project_5` as it's theis stage is only linked to this project.",
        )
        self.assertFalse(
            stage_2.rating_active,
            "`stage_2` should be configured with `project_5` settings (default settings values).",
        )
        self.assertEqual(
            stage_2.rating_status,
            "stage",
            "`stage_2` should be configured with `project_5` settings (default settings values).",
        )
        self.assertEqual(
            stage_2.rating_status_period,
            "monthly",
            "`stage_2` should be configured with `project_5` settings (default settings values).",
        )

        self.assertFalse(
            stage_4.rating_active,
            "As this stage has no rating email template, it should have default settings values.",
        )
        self.assertEqual(
            stage_4.rating_status,
            "stage",
            "As this stage has no rating email template, it should have default settings values.",
        )
        self.assertEqual(
            stage_4.rating_status_period,
            "monthly",
            "As this stage has no rating email template, it should have default settings values.",
        )

        self.assertTrue(
            all(not project.allow_recurring_tasks for project in (projects - project_2)),
            "All projects except `project_2` should have `allow_recurring_tasks` disabled as they contain no recurring task.",
        )
        self.assertTrue(task_2.recurring_task, "`task_2` should still be a recurring task.")
        self.assertTrue(
            project_2.allow_recurring_tasks,
            "Only `project_2` should allow recurring tasks as it contains a recurring task.",
        )

        self.assertEqual(
            task_1.stage_id,
            stage_3,
            "This task belongs to `project_1` and should be kept in `stage_3` as this stage was not duplicated.",
        )
        self.assertEqual(
            task_2.stage_id,
            project_2.type_ids,
            "This task belongs to `project_2` and should be moved to the new stage created for `project_2`.",
        )
        self.assertEqual(
            task_3.stage_id,
            project_3.type_ids,
            " This task belongs to `project_3` and should be moved to the new stage created for `project_3`.",
        )
        self.assertEqual(
            task_4.stage_id,
            project_4.type_ids,
            " This task belongs to `project_4` and should be moved to the new stage created for `project_4`.",
        )
        self.assertEqual(
            task_5.stage_id,
            project_5.type_ids[0],
            " This task belongs to `project_5` and should be moved to the new stage created for `project_5`.",
        )
        self.assertEqual(
            task_6.stage_id,
            project_6.type_ids,
            "This task belongs to `project_6` and should be moved to the new stage created for `project_6`.",
        )
        self.assertEqual(
            task_7.stage_id,
            stage_2,
            "This task belongs to `project_7` and should be kept in `stage_2` as this stage was not duplicated.",
        )
