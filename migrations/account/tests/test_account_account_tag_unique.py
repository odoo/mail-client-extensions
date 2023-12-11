# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class CheckAccountTagUnique(UpgradeCase):
    def prepare(self):
        # case: 1 tag duplicates of 3 and 2 tag is duplicate of 4
        # both duplicates tag use same account in relation table

        # Duplicate Tags: [1, 3], [2, 4]
        # M2M account_account_account_tag table:
        # account_account_tag_id   |  account_account_id
        #        1                      X
        #        3                      x
        #        2                      x
        #        4                      x

        currency = self.env.ref("base.EUR")
        company = self.env["res.company"].create({"name": "company for account test", "currency_id": currency.id})

        account_account_tag1 = self.env["account.account.tag"].create(
            {"name": "Account Tag1", "applicability": "accounts"}
        )

        account_account_tag2 = self.env["account.account.tag"].create(
            {"name": "Account Tag2", "applicability": "accounts"}
        )

        account_account_tag3 = self.env["account.account.tag"].create(
            {"name": "Account Tag1", "applicability": "accounts"}
        )

        account_account_tag4 = self.env["account.account.tag"].create(
            {"name": "Account Tag2", "applicability": "accounts"}
        )

        account_expense_id_1_3_2_4 = self.env["account.account"].create(
            {
                "code": "UNAC001.3.2.4",
                "name": "Stock adjustment for tag1 and tag3",
                "company_id": company.id,
                "account_type": "expense_direct_cost",
                "internal_group": "expense",
                "deprecated": "f",
                "reconcile": "f",
            }
        )

        # create entry in relation `account_account_account_tag` for same account.

        query = "INSERT INTO account_account_account_tag(account_account_id, account_account_tag_id) VALUES (%s, %s)"

        self.env.cr.execute(query, [account_expense_id_1_3_2_4.id, account_account_tag1.id])
        self.env.cr.execute(query, [account_expense_id_1_3_2_4.id, account_account_tag3.id])
        self.env.cr.execute(query, [account_expense_id_1_3_2_4.id, account_account_tag2.id])
        self.env.cr.execute(query, [account_expense_id_1_3_2_4.id, account_account_tag4.id])

        return {
            "account_expense_id_1_3_2_4": account_expense_id_1_3_2_4.id,
            "account_account_tag1": account_account_tag1.id,
            "account_account_tag2": account_account_tag2.id,
            "account_account_tag3": account_account_tag3.id,
            "account_account_tag4": account_account_tag4.id,
        }

    def check(self, init):
        query = """SELECT 1
                     FROM account_account_account_tag
                    WHERE account_account_id = %s
                      AND account_account_tag_id = %s"""

        self.env.cr.execute(query, [init["account_expense_id_1_3_2_4"], init["account_account_tag3"]])
        self.assertFalse(self.env.cr.rowcount, "The duplicate tag3 entry should be deleted after the migration")

        self.env.cr.execute(query, [init["account_expense_id_1_3_2_4"], init["account_account_tag4"]])
        self.assertFalse(self.env.cr.rowcount, "The duplicate tag4 entry should be deleted after the migration")

        self.env.cr.execute(query, [init["account_expense_id_1_3_2_4"], init["account_account_tag1"]])
        self.assertTrue(self.env.cr.rowcount, "tag1 should have been kept, and replaced tag3")

        self.env.cr.execute(query, [init["account_expense_id_1_3_2_4"], init["account_account_tag2"]])
        self.assertTrue(self.env.cr.rowcount, "tag2 should have been kept, and replaced tag4")
