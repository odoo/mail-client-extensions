# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.3")
class TestMigrateMakeBillableProjectIfPartnerSet(UpgradeCase):
    def prepare(self):
        """ """
        partner = self.env["res.partner"].create({"name": "test"})
        project1, project2 = self.env["project.project"].create(
            [
                {"name": "Project with partner", "partner_id": partner.id, "allow_billable": False, "is_fsm": True},
                {"name": "Project without partner", "allow_billable": False, "is_fsm": True},
            ]
        )

        project1_task, project2_task = self.env["project.task"].create(
            [
                {"name": "Task 1 in project 1"},
                {"name": "Task with partner in project 2", "project_id": project2.id},
            ]
        )
        return (project1.id, project2.id)

    def check(self, init):
        project1_id, project2_id = init
        projects = self.env["project.project"].browse([project1_id, project2_id])
        self.assertFalse(
            all(projects.mapped("allow_billable")), "The both fsm projects should not be billable after the migration"
        )
