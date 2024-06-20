from odoo import fields

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestLockDatesRework(UpgradeCase):
    def prepare(self):
        period_lock_date = "2022-01-01"
        company = self.env["res.company"].create(
            {
                "name": "TestLockDatesRework 17.5 upgrade company",
                "period_lock_date": period_lock_date,
            }
        )
        return {
            "company_id": company.id,
            "period_lock_date": period_lock_date,
        }

    def check(self, init):
        old_period_lock_date = fields.Date.from_string(init["period_lock_date"])
        company = self.env["res.company"].browse(init["company_id"])
        self.assertRecordValues(
            company,
            [
                {
                    "sale_lock_date": old_period_lock_date,
                    "purchase_lock_date": old_period_lock_date,
                },
            ],
        )
