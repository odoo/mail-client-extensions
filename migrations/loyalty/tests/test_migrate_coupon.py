from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestMigrateCoupon(UpgradeCase):
    @property
    def key(self):
        return "coupon.tests.test_loyalty.TestLoyalty"

    def prepare(self):
        # The prepare is defined in coupon/tests/test_loyalty.py
        return []

    def check(self, init):
        product_id, discount_product_id, discount_product_10_id, partner_id, _ = init

        product = self.env["product.product"].browse(product_id)
        discount_product = self.env["product.product"].browse(discount_product_id)
        discount_product_10 = self.env["product.product"].browse(discount_product_10_id)
        partner = self.env["res.partner"].browse(partner_id)
        programs = self.env["loyalty.program"].search([("name", "=ilike", "UPGRADE_%")])
        coupon_program = free_product_program = code_discount_program = next_order_program = False
        for program in programs:
            if program.name == "UPGRADE_coupon_program":
                coupon_program = program
            elif program.name == "UPGRADE_free_product_program":
                free_product_program = program
            elif program.name == "UPGRADE_code_discount_program":
                code_discount_program = program
            elif program.name == "UPGRADE_next_order_program":
                next_order_program = program

        self.assertEqual(len(programs), 4, "There should be 4 programs converted")

        # Check coupon program
        coupons = self.env["loyalty.card"].search([("program_id", "=", coupon_program.id)])
        # 3 of our coupons should have a partner
        self.assertEqual(len(coupons.filtered(lambda c: c.partner_id == partner)), 3)
        # 2 of our coupons should have no points
        self.assertEqual(len(coupons.filtered(lambda c: c.points > 0)), 2, "Invalid points on one of the coupon")
        # Check program values
        self.assertEqual(coupon_program.program_type, "coupons", "Invalid program type")
        self.assertEqual(coupon_program.applies_on, "current", "Invalid program applicability")
        self.assertEqual(coupon_program.reward_ids.discount_mode, "percent", "Invalid discount mode")
        self.assertEqual(coupon_program.reward_ids.discount, 10, "Invalid discount percent")

        # Check free product program
        self.assertEqual(free_product_program.program_type, "promotion", "Invalid program type")
        self.assertEqual(free_product_program.applies_on, "current", "Invalid program applicability")
        self.assertEqual(free_product_program.reward_ids.reward_type, "product", "Invalid reward type")
        self.assertEqual(free_product_program.reward_ids.reward_product_id, product, "Invalid reward product")
        self.assertEqual(free_product_program.rule_ids.minimum_qty, 3, "Invalid minimum quantity")
        self.assertEqual(
            free_product_program.rule_ids.product_domain, "[['name','ilike','large cabinet']]", "Invalid product domain"
        )
        self.assertEqual(
            free_product_program.reward_ids.discount_line_product_id, discount_product, "Invalid discount line product"
        )

        # Check code discount program
        self.assertEqual(code_discount_program.program_type, "promo_code", "Invalid Program Type")
        self.assertEqual(code_discount_program.trigger, "with_code", "Invalid program trigger")
        self.assertEqual(code_discount_program.rule_ids.mode, "with_code", "Invalid trigger mode")
        self.assertEqual(code_discount_program.rule_ids.code, "UPGRADE_10pc", "Invalid trigger code")
        self.assertEqual(code_discount_program.applies_on, "current", "Invalid program applicability")
        self.assertEqual(
            code_discount_program.reward_ids.discount_line_product_id,
            discount_product_10,
            "Invalid discount line product",
        )

        # Check next order program
        self.assertEqual(next_order_program.program_type, "promotion", "Invalid program type")
        self.assertEqual(next_order_program.applies_on, "future", "Invalid applicability")
        self.assertEqual(next_order_program.rule_ids.minimum_amount, 100, "Invalid min amount")
        self.assertEqual(
            next_order_program.reward_ids.discount_applicability, "order", "Invalid discount applicability"
        )
        self.assertEqual(next_order_program.reward_ids.discount, 15.0, "Invalid discount %")
