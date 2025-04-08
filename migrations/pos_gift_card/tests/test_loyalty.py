from odoo.fields import Datetime

from odoo.addons.base.maintenance.migrations.account.tests.test_common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~15.3")
class TestLoyalty(TestAccountingSetupCommon):
    def prepare(self):
        # Create a gift card and pay an order with it
        super().prepare()
        journal = self.env["account.journal"].create(
            {"name": "UPG", "code": "UPG", "type": "general", "company_id": self.company.id}
        )
        gift_card = self.env["gift.card"].create(
            {
                "initial_amount": 50,
                "company_id": self.company.id,
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "UPGRADE_test_product",
                "lst_price": 30,
                "property_account_income_id": self.account_income.id,
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
            .with_company(self.company)
            .create(
                {
                    "name": "UPGRADE pos config",
                    "company_id": self.company.id,
                    "sequence_id": sequence.id,
                    "journal_id": journal.id,
                    "payment_method_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "UPGRADE method",
                                "company_id": self.company.id,
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
        ui_data = {
            "name": "UPGRADE sol",
            "user_id": self.env.user.id,
            "pos_session_id": session.id,
            "partner_id": self.partner.id,
            "sequence_number": 1,
            "pricelist_id": self.partner.property_product_pricelist.id,
            "fiscal_position_id": session.config_id.default_fiscal_position_id.id,
            "creation_date": str(Datetime.now()),
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
            "statement_ids": [],
        }

        soid = self.env["pos.order"].create_from_ui([{"data": ui_data}])[0]["id"]
        so = self.env["pos.order"].browse(soid)
        so.action_pos_order_paid()
        r = session.close_session_from_ui()
        self.assertTrue(r["successful"], r.get("message"))
        return (so.id,)

    def check(self, init):
        # The check is defined in pos_loyalty/tests/test_migrate_gift_card.py
        pass
