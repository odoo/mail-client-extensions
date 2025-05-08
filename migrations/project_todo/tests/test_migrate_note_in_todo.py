import contextlib
from datetime import date

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.3")
class TestMigrateNoteInTodo(UpgradeCase):
    @property
    def key(self):
        return "note.tests.test_migrate_note_in_todo.TestMigrateNoteInTodo"

    def prepare(self):
        return []

    def check(self, init):
        key, note_ids, stage_ids, user2_stage_ids, tag_ids, user_id, attachment_ids, user_no_stage_id = init

        personal_stage_ids = []
        project_tag_id = False
        task_id = False
        payroll_note_id = False

        with contextlib.suppress(KeyError):
            personal_stage_ids, project_tag_id, task_id = self._get_value(
                "project.tests.test_migrate_note_in_todo.TestMigrateNoteInTodo"
            )
        with contextlib.suppress(KeyError):
            payroll_note_id = self._get_value(
                "hr_payroll.tests.test_migrate_note_in_payroll_note.TestMigrateNoteInPayrollNote"
            )

        self.env.cr.execute(
            """
                SELECT id
                  FROM ir_model im
                 WHERE im.model IN ('note.note', 'note.stage', 'note.tag')
            """
        )
        self.assertFalse(self.env.cr.rowcount, "The note models should be deleted after the migration")

        if not task_id:
            # no additional check todo since the project module has not been installed and so no note has been migrated
            return

        todos = self.env["project.task"].search([("name", "=ilike", f"{key}_note%")])
        self.assertEqual(
            len(todos),
            len(note_ids),
            "The number of notes migrated in project.task model should be the number of notes to migrate",
        )
        user_using_note = self.env["res.users"].browse(user_id)
        users = self.env.user + user_using_note
        self.assertEqual(todos.user_ids, users, "The owners of the notes migrated should be assigned to the todos")
        current_user_todos = todos.filtered(lambda todo: todo.user_ids == self.env.user)
        self.assertEqual(
            len(current_user_todos), 2, "The 3 notes of the current user should be converted in project.task model"
        )
        user_using_note_todos = todos.filtered(lambda todo: todo.user_ids == user_using_note)
        self.assertEqual(
            len(user_using_note_todos), 1, "The note created by that user should be migrated in project.task model"
        )
        both_users_assigned_todo = todos.filtered(lambda todo: todo.user_ids == users)
        self.assertEqual(
            len(both_users_assigned_todo),
            1,
            "The both users should be assigned to a todo since a note has the current user as owner and the other user in followers.",
        )

        current_user_personal_stages = self.env["project.task.type"].browse(personal_stage_ids)
        for stage in current_user_personal_stages:
            self.assertTrue(
                self.env["project.task.type"].search_count(
                    [
                        ("user_id", "=", self.env.uid),
                        ("name", "=", stage.name),
                        ("sequence", "=", stage.sequence),
                        ("fold", "=", stage.fold),
                    ]
                ),
                f"Expected original stage '{stage.name}' for current user to be preserved after migration",
            )

        stage_names = self.env["project.task.type"].search([("user_id", "=", self.env.uid)]).mapped("name")
        self.assertEqual(
            len(stage_names), len(set(stage_names)), "Duplicate stage names found for the current user after migration"
        )

        self.assertEqual(
            self.env["project.task.type"].search_count([("name", "=ilike", f"{key}_%"), ("user_id", "=", user_id)]),
            len(user2_stage_ids),
            "Note stage should be migrated for user with no personal stages existing in Project",
        )

        user_personal_stages = self.env["project.task.type"].search([("user_id", "=", user_no_stage_id)])

        self.assertEqual(
            len(personal_stage_ids),
            len(user_personal_stages),
            f"The personal stages of User, user {key} 2, should be generated and he should have the same number of personal stages than the current user",
        )

        project_tags = self.env["project.tags"].search([("name", "=ilike", f"{key}_%")])
        test_project_tags = project_tags.filtered(lambda tag: tag.name == f"{key}_test")
        self.assertEqual(
            len(test_project_tags),
            1,
            "The tag in note should not be migrated since the tag name exists in project tags model",
        )
        self.assertEqual(test_project_tags.id, project_tag_id)

        todo_attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "project.task"), ("res_id", "in", todos.ids)]
        )
        self.assertEqual(
            len(todo_attachments),
            len(attachment_ids),
            "The number of attachments linked to notes migrated in project.task model should be the same as before migration",
        )

        todo_with_activity = self.env["project.task"].search([("name", "=", f"{key}_note1")])
        todo_activities = self.env["mail.activity"].search(
            [("res_model", "=", "project.task"), ("res_id", "=", todo_with_activity.id)]
        )
        self.assertEqual(
            len(todo_activities),
            1,
            "Exactly one activity should be planned for the notes converted to project.task records",
        )
        self.assertEqual(
            todo_activities.date_deadline,
            date.fromisoformat("2023-05-20"),
            "The date planned for the activity should not change during upgrade",
        )
        todo_messages = self.env["mail.message"].search(
            [("model", "=", "project.task"), ("res_id", "=", todo_with_activity.id)]
        )
        self.assertEqual(
            len(todo_messages),
            2,  # Automatic creation message and message manually loged during test preparation
            "Exactly one message should be logged for the note converted to project.task record",
        )

        if payroll_note_id:
            payroll_todo = self.env["project.task"].search([("name", "=", "UPGRADE_test_migrate_note_in_payroll_note")])
            self.assertFalse(payroll_todo, "No payroll note should be migrated in project.task model")
