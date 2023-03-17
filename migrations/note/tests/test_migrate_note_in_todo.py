# -*- coding: utf-8 -*-

import base64
from datetime import date

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.3")
class TestMigrateNoteInTodo(UpgradeCase):
    def prepare(self):
        key = "UPGRADE_test_migrate_note_in_todo"
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": f"user {key}",
                    "login": key,
                    "groups_id": [self.env["ir.model.data"]._xmlid_to_res_id("base.group_user")],
                }
            )
        )
        user_no_stage = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": f"user {key} 2",
                    "login": key + " 2",
                    "groups_id": [self.env["ir.model.data"]._xmlid_to_res_id("base.group_user")],
                }
            )
        )
        user.partner_id.email = f"{key}@test.com"
        new_stage, done_stage, user2_new_stage, user2_done_stage = self.env["note.stage"].create(
            [
                {"name": f"{key}_new"},
                {"name": f"{key}_done"},
                {"name": f"{key}_new2", "user_id": user.id},
                {"name": f"{key}_done2", "user_id": user.id},
            ]
        )
        test_tag, upgrade_tag = self.env["note.tag"].create(
            [
                {"name": f"{key}_test"},
                {"name": f"{key}_upgrade"},
            ]
        )
        note, note_upgrade_tag, note_done, note_user_2, note_user_no_stage_1, note_user_no_stage_2 = self.env[
            "note.note"
        ].create(
            [
                {"name": f"{key}_note1", "memo": "test note 1", "stage_id": new_stage.id, "tag_ids": [test_tag.id]},
                {"name": f"{key}_note2", "memo": "test note 2", "stage_id": new_stage.id, "tag_ids": [upgrade_tag.id]},
                {
                    "name": f"{key}_note3",
                    "memo": "test note 3",
                    "stage_id": done_stage.id,
                    "message_partner_ids": [user.partner_id.id],
                },
                {
                    "name": f"{key}_note4",
                    "memo": "test note 4",
                    "stage_id": user2_done_stage.id,
                    "user_id": user.id,
                    "tag_ids": [test_tag.id, upgrade_tag.id],
                },
                {
                    "name": f"{key}_note5",
                    "memo": "test note 5",
                    "user_id": user_no_stage.id,
                },
                {
                    "name": f"{key}_note6",
                    "memo": "test note 6",
                    "user_id": user_no_stage.id,
                },
            ]
        )

        # removin note stage for user 2
        self.env["note.stage"].search([("user_id", "=", user_no_stage.id)]).unlink()

        # Testing text attachments

        TEXT = base64.b64encode(bytes("workflow bridge project", "utf-8"))

        attachment_txt_test = self.env["ir.attachment"].create(
            {
                "datas": TEXT,
                "name": "fileText_test.txt",
                "mimetype": "text/plain",
                "res_model": "note.note",
                "res_id": note.id,
            }
        )

        # Testing activity planning

        note.activity_schedule(
            activity_type_id=self.env["mail.activity.type"].search([("category", "=", "reminder")], limit=1).id,
            note="Activity planned for test note 1",
            date_deadline=date.fromisoformat("2023-05-20"),
        )

        # Testing chatter

        note.message_post(body="Message posted on the chatter of <b>note test 1</b>", author_id=user.partner_id.id)

        all_notes = note + note_upgrade_tag + note_done + note_user_2 + note_user_no_stage_1 + note_user_no_stage_2
        stages = new_stage + done_stage
        user2_stages = user2_new_stage + user2_done_stage
        note_tags = test_tag + upgrade_tag
        all_attachments = attachment_txt_test

        return (
            key,
            all_notes.ids,
            stages.ids,
            user2_stages.ids,
            note_tags.ids,
            user.id,
            all_attachments.ids,
            user_no_stage.id,
        )

    def check(self, init):
        # The check is done in migrations/project_todo/tests/test_migration_note_in_todo.py
        return
