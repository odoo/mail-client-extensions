import contextlib
from datetime import datetime

with contextlib.suppress(ImportError):
    from odoo import Command

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestMigrateProjectTaskToProjectTaskTemplate(UpgradeCase):
    def prepare(self):
        if util.column_exists(self.env.cr, "project_task", "is_template"):
            """ The user"s recurring groups aren"t being set. During the stock module tests, the
            settings change, which turns recurring tasks into non-recurring ones. So I have to activated.
            """
            self.env["res.config.settings"].create({"group_project_recurring_tasks": True}).execute()

            partner = self.env["res.partner"].create(
                {
                    "name": "Test Lelitre",
                    "email": "Test.lelitre@agrolait.com",
                }
            )

            Users = self.env["res.users"].with_context({"no_reset_password": True})

            # Create a project user
            user_projectuser = Users.create(
                {
                    "name": "TestProjectUser",
                    "login": "TestarmandeRD",
                    "password": "TestarmandelRD",
                    "email": "Testprojectuser11@example.com",
                }
            )

            # Create a project manager user
            user_projectmanager = Users.create(
                {
                    "name": "TestProjectManager",
                    "login": "Testbastien1345",
                    "email": "Testprojectmanager11@example.com",
                }
            )

            # Create two projects
            project1, project2 = (
                self.env["project.project"]
                .with_context(mail_create_nolog=True)
                .create(
                    [
                        {"name": "Project 1"},
                        {"name": "Project 2"},
                    ]
                )
            )

            # Create tags and assign to project1
            project_tags = self.env["project.tags"].create(
                [
                    {"name": "RD-HR", "project_ids": [Command.link(project1.id)]},
                    {"name": "RD-Service", "project_ids": [Command.link(project1.id)]},
                ]
            )

            # Create milestone linked to project1
            milestone = self.env["project.milestone"].create({"name": "Milestone 1", "project_id": project1.id})

            # Create a parent task with child template tasks
            self.env["project.task"].with_context(mail_create_nolog=True).create(
                {
                    "name": "RD Parent Task",
                    "project_id": project1.id,
                    "is_template": True,
                    "child_ids": [
                        Command.create({"is_template": True, "name": "RD Sub-Task", "project_id": project1.id}),
                        Command.create(
                            {
                                "is_template": True,
                                "name": "RD Sub-Task2",
                                "project_id": project1.id,
                                "display_in_project": True,
                            }
                        ),
                        Command.create({"is_template": True, "name": "RD Sub-Task3", "project_id": project2.id}),
                    ],
                }
            )

            # Create the main template task with tags, users, and milestone
            self.env["project.task"].with_context(mail_create_nolog=True).create(
                {
                    "name": "RD Task",
                    "project_id": project1.id,
                    "partner_id": partner.id,
                    "recurring_task": True,
                    "date_deadline": "2020-01-01",
                    "repeat_interval": 2,
                    "repeat_unit": "month",
                    "repeat_type": "forever",
                }
            )

            # Create the main template task with tags, users, and milestone
            task_template = (
                self.env["project.task"]
                .with_context(mail_create_nolog=True)
                .create(
                    {
                        "name": "RD Task Template",
                        "project_id": project1.id,
                        "partner_id": partner.id,
                        "milestone_id": milestone.id,
                        "is_template": True,
                        "recurring_task": True,
                        "date_deadline": "2020-01-01",
                        "repeat_interval": 2,
                        "repeat_unit": "month",
                        "repeat_type": "forever",
                        "tag_ids": [Command.set(project_tags.ids)],
                        "user_ids": [Command.set([user_projectuser.id, user_projectmanager.id])],
                    }
                )
            )

            worksheet_template_id = False

            if util.module_installed(self.env.cr, "hr_timesheet"):
                task_template.allocated_hours = 20
            if util.module_installed(self.env.cr, "industry_fsm_report"):
                worksheet_template_id = (
                    self.env["worksheet.template"]
                    .create(
                        {
                            "name": "Test Default Worksheet",
                            "res_model": "project.task",
                        }
                    )
                    .id
                )

                task_template.worksheet_template_id = worksheet_template_id

            # Create a task with dependencies
            self.env["project.task"].with_context(mail_create_nolog=True).create(
                {
                    "name": "RD Depend Task",
                    "is_template": True,
                    "project_id": project1.id,
                    "depend_on_ids": [
                        Command.create({"is_template": True, "name": "RD Sub Depend Task", "project_id": project1.id}),
                    ],
                }
            )

            return {
                "projects": (project1 + project2).ids,
                "milestone": milestone.id,
                "user_projectmanager": user_projectmanager.id,
                "user_projectuser": user_projectuser.id,
                "project_tags": project_tags.ids,
                "worksheet_template_id": worksheet_template_id,
            }
        return {}

    def check(self, init):
        if init and util.table_exists(self.env.cr, "project_task_template"):
            # Validate the migrated template task
            task_template = self.env["project.task.template"].search([("name", "=", "RD Task Template")])
            # Check if recurring task is set properly
            self.assertEqual(task_template.name, "RD Task Template")

            # Check repeat unit
            self.assertEqual(task_template.repeat_unit, "month", "Repeat unit should be 'month'")
            # Check repeat interval
            self.assertEqual(task_template.repeat_interval, 2, "Repeat interval should be 2")
            # Check repeat type
            self.assertEqual(task_template.repeat_type, "forever", "Repeat type should be 'forever'")
            # Check that the task deadline is correctly set
            self.assertEqual(
                task_template.date_deadline,
                datetime(2020, 1, 1),
                "The deadline on the task template does not match the expected date",
            )
            self.assertTrue(task_template.recurring_task, "Task template should be marked as a recurring task")

            # Check milestone is correctly linked
            self.assertEqual(
                task_template.milestone_id.id, init.get("milestone"), "Milestone ID does not match the expected value"
            )

            # Check project is one of the original projects
            self.assertIn(
                task_template.project_id.id, init.get("projects"), "Project ID is not in the expected project list"
            )

            # Check tag IDs match
            self.assertCountEqual(task_template.tag_ids.ids, init.get("project_tags"), "Tag IDs do not match")
            # Check user IDs match
            self.assertCountEqual(
                task_template.user_ids.ids,
                [init.get("user_projectuser"), init.get("user_projectmanager")],
                "User IDs do not match",
            )

            # Check parent task and its child tasks
            parent_task = self.env["project.task.template"].search([("name", "=", "RD Parent Task")])

            self.assertIn(
                parent_task.project_id.id,
                init.get("projects"),
                "Parent task project ID is not in the expected project list",
            )

            # Check child task 3 (Sub-Task)
            self.assertEqual(parent_task.child_ids[2].name, "RD Sub-Task", "Child task 3 name mismatch")
            self.assertIn(
                parent_task.child_ids[2].project_id.id,
                init.get("projects"),
                "Child task 3 project ID is not in the expected project list",
            )

            # Check child task 2 (Sub-Task2)
            self.assertEqual(parent_task.child_ids[1].name, "RD Sub-Task2", "Child task 2 name mismatch")
            self.assertIn(
                parent_task.child_ids[1].project_id.id,
                init.get("projects"),
                "Child task 2 project ID is not in the expected project list",
            )

            # Check child task 1 (Sub-Task3)
            self.assertEqual(parent_task.child_ids[0].name, "RD Sub-Task3", "Child task 1 name mismatch")
            self.assertIn(
                parent_task.child_ids[0].project_id.id,
                init.get("projects"),
                "Child task 1 project ID is not in the expected project list",
            )

            # Check allocated hours if the hr_timesheet module is installed
            if util.module_installed(self.env.cr, "hr_timesheet"):
                self.assertEqual(
                    task_template.allocated_hours, 20, "Allocated hours not set correctly in task template"
                )

            # Check worksheet template if the industry_fsm_report module is installed
            if util.module_installed(self.env.cr, "industry_fsm_report"):
                self.assertEqual(
                    task_template.worksheet_template_id.id,
                    init.get("worksheet_template_id"),
                    "Worksheet template ID not set correctly in task template",
                )
