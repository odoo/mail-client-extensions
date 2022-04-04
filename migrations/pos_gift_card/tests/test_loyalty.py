# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class TestLoyalty(UpgradeCase):
    def prepare(self):
        # Create a gift card and pay an order with it
        company = self.env["res.company"].create(
            {
                "name": "UPGRADE_company",
            }
        )
        gift_card = self.env["gift.card"].create(
            {
                "initial_amount": 50,
                "company_id": company.id,
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
        sequence = self.env["ir.sequence"].create(
            {
                "name": "UPGRADE sequence",
                "implementation": "standard",
            }
        )
        config = (
            self.env["pos.config"]
            .with_company(company)
            .create(
                {
                    "name": "UPGRADE pos config",
                    "company_id": company.id,
                    "sequence_id": sequence.id,
                    "payment_method_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "UPGRADE method",
                                "company_id": company.id,
                                "split_transactions": True,
                            },
                        )
                    ],
                }
            )
        )
        config.open_session_cb()
        session = config.current_session_id
        pay_with_gift_card = self.env.ref("gift_card.pay_with_gift_card_product")
        so = self.env["pos.order"].create(
            {
                "name": "UPGRADE sol",
                "partner_id": partner.id,
                "session_id": session.id,
                "amount_tax": 4.5,
                "amount_total": 0,
                "amount_paid": 0,
                "amount_return": 0,
                "lines": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "qty": 1,
                            "price_unit": 30,
                            "price_subtotal": 30,
                            "price_subtotal_incl": 34.5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": pay_with_gift_card.id,
                            "gift_card_id": gift_card.id,
                            "qty": 1,
                            "price_unit": -34.5,
                            "price_subtotal": -34.5,
                            "price_subtotal_incl": -34.5,
                        },
                    ),
                ],
            }
        )
        so.state = "paid"
        return (so.id,)

    def check(self, init):
        # The check is defined in pos_loyalty/tests/test_migrate_gift_card.py
        pass
