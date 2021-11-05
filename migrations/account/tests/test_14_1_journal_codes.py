# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.1")
class TestJournalCodes(UpgradeCase):
    def prepare(self):
        journal_ids = []
        test_codes = ["TEST1", "TEST1", "TEST1", "SALES", "SALES", "SOLO"]
        for i, code in enumerate(test_codes):
            new_journal = self.env["account.journal"].create(
                {
                    "name": "Test Journal %s" % i,
                    "code": code,
                    "type": "general",
                }
            )

            journal_ids.append(new_journal.id)

        return {"test_journal_codes": journal_ids}

    def check(self, init):
        expected_codes = ["TEST1", "TEST2", "TEST3", "SALES", "SALE1", "SOLO"]
        journal_codes = self.env["account.journal"].browse(init["test_journal_codes"]).mapped("code")
        self.assertEqual(journal_codes, expected_codes)
