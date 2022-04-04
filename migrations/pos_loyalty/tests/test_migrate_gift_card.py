# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestMigrateCoupon(UpgradeCase):
    @property
    def key(self):
        return "pos_gift_card.tests.test_loyalty.TestLoyalty"

    def _key_exists(self, key):
        # Avoid a warning
        return False

    def _set_value(self, key, value):
        # Completely ignore the prepare from this class, only use the one from
        #  `pos_gift_card`
        return

    def prepare(self):
        # The prepare is defined in pos_gift_card/tests/test_loyalty.py
        return []

    def check(self, init):
        so_id = init

        so = self.env["pos.order"].browse(so_id)
        coupon = so.lines.coupon_id
        self.assertTrue(coupon, "There should be a coupon")
        self.assertEqual(
            coupon.points,
            50 - so.lines.filtered(lambda l: not l.coupon_id).price_subtotal_incl,
            "The inital value was 50 but it should be 20 now",
        )
