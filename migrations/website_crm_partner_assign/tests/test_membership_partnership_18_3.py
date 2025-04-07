from dateutil.relativedelta import relativedelta

try:
    from odoo import Command, fields
except ImportError:
    # `Command` is only available in recent versions
    Command = fields = None

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.3")
class TestPartnershipUpgrade(UpgradeCase):
    def prepare(self):
        if not util.module_installed(self.cr, "membership"):
            self.skipTest("Membership not installed")
        now = fields.Datetime.now()
        membership = self.env["product.product"].create(
            {
                "name": "Membership",
                "membership": True,
                "membership_date_from": now + relativedelta(months=-3),
                "membership_date_to": now + relativedelta(months=+2),
            }
        )
        grade = self.env["res.partner.grade"].create(
            {
                "name": "Gold partner",
            }
        )
        partner = self.env["res.partner"].create(
            {
                "name": "partner",
                "grade_id": grade.id,
            },
        )
        self.env["account.move"].create(
            {
                "partner_id": partner.id,
                "move_type": "out_invoice",
                "date": now.date(),
                "line_ids": [
                    Command.create(
                        {
                            "product_id": membership.id,
                        },
                    )
                ],
            },
        )
        return {
            "grade": grade.id,
            "partner": partner.id,
        }

    def check(self, init):
        partner = self.env["res.partner"].browse(init["partner"])
        grade = self.env["res.partner.grade"].browse(init["grade"])
        self.assertEqual(partner.grade_id, grade)
        self.assertIn("Membership history", partner.message_ids[0].body)
