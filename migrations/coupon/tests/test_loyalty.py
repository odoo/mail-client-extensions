# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestLoyalty(UpgradeCase):
    def prepare(self):
        # Basic programs
        product, discount_product, discount_product_10 = self.env["product.product"].create(
            [
                {
                    "name": "UPGRADE_PRODUCT",
                    "lst_price": 50,
                },
                {
                    "name": "UPGRADE_FREE_PRODUCT_LINE",
                    "lst_price": 0,
                },
                {
                    "name": "UPGRADE_10%_DISCOUNT",
                    "lst_price": 0,
                },
            ]
        )
        partner = self.env["res.partner"].create(
            {
                "name": "UPGRADE MAN",
            }
        )
        coupon_program = self.env["coupon.program"].create(
            {
                "name": "UPGRADE_coupon_program",
                "promo_code_usage": "code_needed",
                "discount_apply_on": "on_order",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "program_type": "coupon_program",
            }
        )
        self.env["coupon.coupon"].create(
            [
                {
                    "state": "used",
                    "partner_id": partner.id,
                    "program_id": coupon_program.id,
                },
                {
                    "state": "cancel",
                    "partner_id": partner.id,
                    "program_id": coupon_program.id,
                },
                {
                    "state": "new",
                    "partner_id": partner.id,
                    "program_id": coupon_program.id,
                },
                {
                    "state": "new",
                    "program_id": coupon_program.id,
                },
            ]
        )
        free_product_program = self.env["coupon.program"].create(
            {
                "name": "UPGRADE_free_product_program",
                "promo_code_usage": "no_code_needed",
                "discount_apply_on": "on_order",
                "reward_type": "product",
                "program_type": "promotion_program",
                "reward_product_id": product.id,
                "rule_min_quantity": 3,
                "rule_products_domain": "[['name','ilike','large cabinet']]",
                "discount_line_product_id": discount_product.id,
                "validity_duration": 0,
            }
        )
        code_discount_program = self.env["coupon.program"].create(
            {
                "name": "UPGRADE_code_discount_program",
                "promo_code_usage": "code_needed",
                "promo_code": "UPGRADE_10pc",
                "discount_apply_on": "on_order",
                "discount_type": "percentage",
                "discount_percentage": 10.0,
                "program_type": "promotion_program",
                "discount_line_product_id": discount_product_10.id,
                "validity_duration": 0,
            }
        )
        next_order_program = self.env["coupon.program"].create(
            {
                "name": "UPGRADE_next_order_program",
                "program_type": "promotion_program",
                "promo_applicability": "on_next_order",
                "promo_code_usage": "no_code_needed",
                "rule_minimum_amount": 100,
                "discount_apply_on": "on_order",
                "discount_type": "percentage",
                "discount_percentage": 15.0,
                "validity_duration": 0,
            }
        )

        all_programs = coupon_program | free_product_program | code_discount_program | next_order_program
        return (
            product.id,
            discount_product.id,
            discount_product_10.id,
            partner.id,
            all_programs.ids,
        )

    def check(self, init):
        # The check is done in migrations/loyalty/tests/test_migrate_coupon.py
        return
