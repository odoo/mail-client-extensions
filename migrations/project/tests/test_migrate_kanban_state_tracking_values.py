# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.2")
class TestMigrateKanbanStateTrackingValues(UpgradeCase):
    def prepare(self):
        stage = self.env["project.task.type"].create(
            {
                "name": "Stage A",
                "legend_blocked": "I'm blocked",
                "legend_done": "I'm done",
                "legend_normal": "I'm normal",
            }
        )
        project = self.env["project.project"].create(
            {
                "name": "Project 1",
                "type_ids": stage.ids,
            }
        )
        task = self.env["project.task"].create(
            {
                "name": "Task 1",
                "project_id": project.id,
                "stage_id": stage.id,
            }
        )

        # flush trackings
        self.cr.flush()

        task.kanban_state = "blocked"
        self.cr.flush()

        task.kanban_state = "done"
        self.cr.flush()

        kanban_state_label_field = self.env["ir.model.fields"].search(
            [("name", "=", "kanban_state_label"), ("model", "=", "project.task")]
        )
        blocked_tracking, done_tracking = self.env["mail.tracking.value"].search(
            [
                ("mail_message_id", "in", task.message_ids.ids),
                ("field", "=", kanban_state_label_field.id),
            ],
            order="id",
        )
        return (task.id, blocked_tracking.id, done_tracking.id)

    def check(self, init):
        task_id, blocked_tracking_id, done_tracking_id = init
        trackings = self.env["mail.tracking.value"].browse([blocked_tracking_id, done_tracking_id])
        state_field = self.env["ir.model.fields"].search([("name", "=", "state"), ("model", "=", "project.task")])
        self.assertTrue(trackings.exists())

        blocked_tracking, done_tracking = trackings
        tracking_fname = "field_id" if util.column_exists(self.cr, "mail_tracking_value", "field_id") else "field"
        self.assertEqual(
            blocked_tracking[tracking_fname],
            state_field,
            "The field linked to the tracking should now be the state field",
        )
        self.assertEqual(
            blocked_tracking.old_value_char,
            "I'm normal",
            "The old value stored in the tracking value should be unchanged",
        )
        self.assertEqual(
            blocked_tracking.new_value_char,
            "I'm blocked",
            "The new value stored in the tracking value should be unchanged",
        )

        self.assertEqual(
            done_tracking[tracking_fname], state_field, "The field linked to the tracking should now be the state field"
        )
        self.assertEqual(
            done_tracking.old_value_char,
            "I'm blocked",
            "The old value stored in the tracking value should be unchanged",
        )
        self.assertEqual(
            done_tracking.new_value_char, "I'm done", "The new value stored in the tracking value should be unchanged"
        )
