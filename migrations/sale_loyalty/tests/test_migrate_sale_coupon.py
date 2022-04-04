from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestLoyalty(UpgradeCase):
    @property
    def key(self):
        return "sale_coupon.tests.test_loyalty.TestLoyalty"

    def prepare(self):
        # The prepare is defined in sale_coupon/tests/test_loyalty.py
        return []

    def check(self, init):
        (so_id,) = init

        so = self.env["sale.order"].browse(so_id)
        self.assertEqual(len(so.order_line), 2, "Invalid order")
        self.assertTrue(so.coupon_point_ids, "coupon_point_ids should be populated")
        self.assertTrue(so.order_line.coupon_id, "A coupon should be linked to the reward line")
