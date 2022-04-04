# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestMigrateCoupon(UpgradeCase):
    @property
    def key(self):
        return "gift_card.tests.test_loyalty.TestLoyalty"

    def prepare(self):
        # The prepare is defined in gift_card/tests/test_loyalty.py
        return ()

    def check(self, init):
        (company_ids,) = init

        companies = self.env["res.company"].browse(company_ids)
        programs = self.env["loyalty.program"].search([("company_id", "in", companies.ids)])
        # A program should have been generated for each company that had gift cards
        self.assertEqual(len(programs), 2, "There should be only 2 programs")
        # Program with company 0 should have 1 gift card
        self.assertEqual(programs.filtered(lambda p: p.company_id == companies[0]).coupon_count, 1)
        # Program with company 1 should have 2 gift card
        self.assertEqual(programs.filtered(lambda p: p.company_id == companies[1]).coupon_count, 2)

        # Check the validity of the program
        program = programs[0]
        self.assertEqual(program.program_type, "gift_card", "Invalid program type")
        self.assertEqual(program.applies_on, "future", "Invalid program applicability")
        self.assertEqual(program.trigger, "auto", "Invalid program trigger")
        gift_card_product = self.env.ref("loyalty.gift_card_product_50")
        gift_card_pay_product = self.env.ref("loyalty.pay_with_gift_card_product")
        self.assertEqual(program.rule_ids.product_ids, gift_card_product, "Invalid trigger product")
        self.assertEqual(
            program.reward_ids.discount_line_product_id, gift_card_pay_product, "Invalid reward discount line"
        )
