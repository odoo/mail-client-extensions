from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.3")
class TestMigrateNoteInTodo(UpgradeCase):
    def prepare(self):
        if not util.module_installed(self.env.cr, "note"):
            self.skipTest("`note` module not installed")
        self.env["project.task"].create(
            {
                "name": "Mystery task",
            }
        )
        personal_stages = self.env["project.task.type"].search([("user_id", "=", self.env.uid)])
        project_tag = self.env["project.tags"].create({"name": "UPGRADE_test_migrate_note_in_todo_test"})
        task = self.env["project.task"].create({"name": "Private Task", "personal_stage_id": personal_stages[-1].id})

        return (
            personal_stages.ids,
            project_tag.id,
            task.id,
        )

    def check(self, init):
        # will be done in migrations/project_todo/tests/test_migrate_note_in_todo.py
        return
