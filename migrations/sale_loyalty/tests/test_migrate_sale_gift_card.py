# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestMigrateSaleGiftCard(UpgradeCase):
    @property
    def key(self):
        return "sale_gift_card.tests.test_loyalty.TestLoyalty"

    def prepare(self):
        # The prepare is defined in sale_gift_card/tests/test_loyalty.py
        return []

    def check(self, init):
        so_id = init

        so = self.env["sale.order"].browse(so_id)
        coupon = so.order_line.coupon_id
        self.assertTrue(coupon, "There should be a coupon")
        self.assertEqual(
            coupon.points,
            50 - so.order_line.filtered(lambda l: not l.coupon_id).price_total,
            "The inital value was 50 but it should be 20 now",
        )
