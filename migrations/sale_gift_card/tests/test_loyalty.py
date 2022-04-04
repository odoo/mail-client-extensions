# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestLoyalty(UpgradeCase):
    def prepare(self):
        # Create a gift card and pay an order with it
        gift_card = self.env["gift.card"].create(
            {
                "initial_amount": 50,
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "UPGRADE_test_product",
                "lst_price": 30,
            }
        )
        partner = self.env["res.partner"].create(
            {
                "name": "UPGRADE MAN",
            }
        )
        so = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        so._pay_with_gift_card(gift_card)
        so.action_confirm()
        so.action_done()
        return (so.id,)

    def check(self, init):
        # The check is defined in sale_loyalty/tests/test_migrate_sale_gift_card.py
        pass
