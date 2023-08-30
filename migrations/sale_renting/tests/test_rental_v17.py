from dateutil.relativedelta import relativedelta

try:
    from odoo import Command, fields
except ImportError:
    # `Command` is only available in recent versions
    Command = fields = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class TestSingleRentalPeriod(UpgradeCase):
    def prepare(self):
        company = self.env["res.company"].create(
            {
                "name": "Renting Company",
            }
        )
        computer = self.env["product.product"].create(
            {
                "name": "Computer",
                "list_price": 2000,
                "rent_ok": True,
            }
        )
        recurrence_hour = self.env["sale.temporal.recurrence"].create(
            {
                "duration": 1,
                "unit": "hour",
            }
        )
        self.env["product.pricing"].create(
            [
                {
                    "recurrence_id": recurrence_hour.id,
                    "price": 3.5,
                    "product_template_id": computer.product_tmpl_id.id,
                },
            ]
        )
        partner = self.env["res.partner"].create(
            {
                "name": "partner",
            }
        )
        follower = self.env["res.partner"].create(
            {
                "name": "follower",
            }
        )
        tags = ("tag 1", "tag 2")
        follower_subtype = "rental"
        so1 = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "company_id": company.id,
                "tag_ids": [Command.create({"name": tag}) for tag in tags],
                "message_follower_ids": [
                    Command.create(
                        {
                            "partner_id": follower.id,
                            "subtype_ids": [Command.create({"name": follower_subtype})],
                            "res_model": "sale.order",
                        }
                    )
                ],
            }
        )
        now = fields.Datetime.now()
        sol1 = self.env["sale.order.line"].create(
            {
                "order_id": so1.id,
                "product_id": computer.id,
                "product_uom_qty": 3,
                "start_date": now + relativedelta(days=-10),
                "return_date": now + relativedelta(days=-3),
                "is_rental": True,
            }
        )
        sol2 = self.env["sale.order.line"].create(
            {
                "order_id": so1.id,
                "product_id": computer.id,
                "product_uom_qty": 2,
                "start_date": now + relativedelta(days=1),
                "return_date": now + relativedelta(days=3),
                "qty_delivered": 2,
                "qty_returned": 2,
                "is_rental": True,
            }
        )
        sol3 = self.env["sale.order.line"].create(
            {
                "order_id": so1.id,
                "product_id": computer.id,
                "product_uom_qty": 2,
                "start_date": now + relativedelta(days=-9),
                "return_date": now + relativedelta(days=3),
                "qty_delivered": 2,
                "qty_returned": 1,
                "is_rental": True,
            }
        )
        sol4 = self.env["sale.order.line"].create(
            {
                "order_id": so1.id,
                "product_id": computer.id,
                "product_uom_qty": 1,
                "is_rental": False,
            }
        )
        return {
            "so1": {
                "id": so1.id,
                "partner": partner.id,
                "company": company.id,
                "tags": tags,
                "follower": follower.id,
                "subtype": follower_subtype,
            },
            "sol1": {"id": sol1.id, "price": sol1.price_total, "order": so1.id},
            "sol2": {"id": sol2.id, "price": sol2.price_total, "order": so1.id},
            "sol3": {"id": sol3.id, "price": sol3.price_total, "order": so1.id},
            "sol4": {"id": sol4.id, "price": sol4.price_total, "order": so1.id},
        }

    def check(self, init):
        # order1: no change in SO generic fields
        so1 = self.env["sale.order"].browse(init["so1"]["id"])
        self.assertEqual(so1.partner_id.id, init["so1"]["partner"])
        self.assertEqual(so1.company_id.id, init["so1"]["company"])
        self.assertEqual(set([tag.name for tag in so1.tag_ids]), set(init["so1"]["tags"]))
        self.assertEqual(so1.message_follower_ids.partner_id.id, init["so1"]["follower"])
        self.assertEqual([subtype.name for subtype in so1.message_follower_ids.subtype_ids][0], init["so1"]["subtype"])

        # line1: remained on same SO, price unchanged
        sol1 = self.env["sale.order.line"].browse(init["sol1"]["id"])
        self.assertEqual(sol1.order_id.id, init["sol1"]["order"])
        self.assertEqual(sol1.price_total, init["sol1"]["price"])

        # line2: moved to other SO, price unchanged, SO has same info
        sol2 = self.env["sale.order.line"].browse(init["sol2"]["id"])
        self.assertNotEqual(sol2.order_id.id, init["sol2"]["order"])
        self.assertEqual(sol2.price_total, init["sol2"]["price"])
        self.assertEqual(sol2.order_id.partner_id.id, init["so1"]["partner"])
        self.assertEqual(sol2.order_id.company_id.id, init["so1"]["company"])
        self.assertEqual(set([tag.name for tag in sol2.order_id.tag_ids]), set(init["so1"]["tags"]))
        self.assertEqual(sol2.order_id.message_follower_ids.partner_id.id, init["so1"]["follower"])
        self.assertEqual(
            [subtype.name for subtype in sol2.order_id.message_follower_ids.subtype_ids][0], init["so1"]["subtype"]
        )

        # line3: moved to other SO, not the same as line2, price unchanged, SO has same info
        sol3 = self.env["sale.order.line"].browse(init["sol3"]["id"])
        self.assertNotEqual(sol3.order_id.id, init["sol3"]["order"])
        self.assertNotEqual(sol3.order_id.id, sol2.order_id.id)
        self.assertEqual(sol3.price_total, init["sol3"]["price"])
        self.assertEqual(sol3.order_id.partner_id.id, init["so1"]["partner"])
        self.assertEqual(sol3.order_id.company_id.id, init["so1"]["company"])
        self.assertEqual(set([tag.name for tag in sol3.order_id.tag_ids]), set(init["so1"]["tags"]))
        self.assertEqual(sol3.order_id.message_follower_ids.partner_id.id, init["so1"]["follower"])
        self.assertEqual(
            [subtype.name for subtype in sol3.order_id.message_follower_ids.subtype_ids][0], init["so1"]["subtype"]
        )

        # line4: remained on same SO, price unchanged
        sol4 = self.env["sale.order.line"].browse(init["sol4"]["id"])
        self.assertEqual(sol4.order_id.id, init["sol4"]["order"])
        self.assertEqual(sol4.price_total, init["sol4"]["price"])
