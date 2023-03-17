# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.3")
class TestMigrateNoteInPayrollNote(UpgradeCase):
    def prepare(self):
        payroll_note_tag = self.env.ref("hr_payroll.payroll_note_tag")
        payroll_note = self.env["note.note"].create(
            {
                "tag_ids": [payroll_note_tag.id],
                "name": "UPGRADE_test_migrate_note_in_payroll_note",
                "memo": "compute payslip",
                "company_id": self.env.company.id,
            }
        )
        return [payroll_note.id]

    def check(self, init):
        payroll_note = self.env["hr.payroll.note"].search([("name", "=", "UPGRADE_test_migrate_note_in_payroll_note")])
        self.assertEqual(len(payroll_note), 1, "The payroll note should be migrated in the new model for payroll app")
