from dateutil.relativedelta import relativedelta

try:
    from odoo import Command, fields
except ImportError:
    # `Command` is only available in recent versions
    Command = fields = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.3")
class TestPartnershipUpgrade(UpgradeCase):
    def prepare(self):
        now = fields.Datetime.now()
        membership = self.env["product.product"].create(
            {
                "name": "Membership",
                "membership": True,
                "membership_date_from": now + relativedelta(months=-3),
                "membership_date_to": now + relativedelta(months=+2),
            }
        )
        old_membership = self.env["product.product"].create(
            {
                "name": "Old Membership",
                "membership": True,
                "membership_date_from": now + relativedelta(months=-10),
                "membership_date_to": now + relativedelta(months=-2),
                "active": False,
            }
        )
        old_membership.product_tmpl_id.active = False
        partner1, partner2, partner3 = self.env["res.partner"].create(
            [
                {
                    "name": "partner 1",
                },
                {
                    "name": "partner 2",
                },
                {
                    "name": "partner 3",
                },
            ]
        )
        self.env["account.move"].create(
            [
                {
                    "partner_id": partner1.id,
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
                {
                    "partner_id": partner2.id,
                    "move_type": "out_invoice",
                    "date": now.date(),
                    "line_ids": [
                        Command.create(
                            {
                                "product_id": old_membership.id,
                            },
                        )
                    ],
                },
            ]
        )
        return {
            "membership": membership.id,
            "old_membership": old_membership.id,
            "partner1": partner1.id,
            "partner2": partner2.id,
            "partner3": partner3.id,
        }

    def check(self, init):
        # The check is defined in partnership/tests/test_membership_partnership_18_3.py
        pass
