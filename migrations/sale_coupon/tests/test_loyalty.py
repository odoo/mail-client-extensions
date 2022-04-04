from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestLoyalty(UpgradeCase):
    def prepare(self):
        # Test that a promotion program that applies to the current order generates a used coupon
        product, discount_product = self.env["product.product"].create(
            [
                {
                    "name": "UPGRADE_PRODUCT",
                    "lst_price": 50,
                },
                {
                    "name": "UPGRADE_FREE_PRODUCT_LINE",
                    "lst_price": 0,
                },
            ]
        )
        free_product_program = self.env["coupon.program"].create(
            {
                "name": "free_product_program",
                "promo_code_usage": "no_code_needed",
                "discount_apply_on": "on_order",
                "reward_type": "product",
                "program_type": "promotion_program",
                "reward_product_id": product.id,
                "rule_min_quantity": 3,
                "rule_products_domain": "[['id','=',%s]]" % product.id,
                "discount_line_product_id": discount_product.id,
                "validity_duration": 0,
            }
        )
        # Avoid polution from other programs
        other_programs = self.env["coupon.program"].search([("id", "!=", free_product_program.id)])
        other_programs.active = False

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
                            "product_uom_qty": 4,
                        },
                    )
                ],
            }
        )
        so.recompute_coupon_lines()
        other_programs.active = True
        so.action_confirm()
        so.action_done()
        return (so.id,)

    def check(self, init):
        # The check is defined in sale_loyalty/tests/test_migrate_sale_coupon.py
        pass
