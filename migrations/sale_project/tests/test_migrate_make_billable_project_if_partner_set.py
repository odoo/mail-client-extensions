# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.3")
class TestMigrateMakeBillableProjectIfPartnerSet(UpgradeCase):
    def prepare(self):
        """ """
        partner = self.env["res.partner"].create({"name": "test"})
        project1, project2, project3 = self.env["project.project"].create(
            [
                {"name": "Project with partner", "partner_id": partner.id, "allow_billable": False},
                {"name": "Project without partner", "allow_billable": False},
                {"name": "Project 2 without partner", "allow_billable": False},
            ]
        )

        project1_task, project2_task, project3_task = self.env["project.task"].create(
            [
                {"name": "Task 1 in project 1"},
                {"name": "Task without partner in project 2", "project_id": project2.id},
                {"name": "Task with partner in project 3", "project_id": project3.id, "partner_id": partner.id},
            ]
        )
        return (project1.id, project2.id, project3.id)

    def check(self, init):
        project1_id, project2_id, project3_id = init
        Project = self.env["project.project"]
        project1 = Project.browse(project1_id)
        self.assertTrue(
            project1.allow_billable, "The project should be billable after the migration since a partner is set"
        )
        project2 = Project.browse(project2_id)
        self.assertFalse(
            project2.allow_billable,
            "The project should stay be non-billable since no partner is set and no one of its tasks has a partner set.",
        )
        project3 = Project.browse(project3_id)
        self.assertTrue(
            project3.allow_billable,
            "The project should be billable after the migration since a partner is set in one of its tasks",
        )
