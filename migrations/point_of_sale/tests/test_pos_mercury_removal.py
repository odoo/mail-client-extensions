from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import module_installed
from odoo.addons.base.maintenance.migrations.util.accounting import no_fiscal_lock


@change_version("saas~17.5")
class TestMercuryRemoval(UpgradeCase):
    def _create_order_with_payment(self, session, vals):
        product = self.env["product.product"].create(
            {
                "name": "Mercury test product",
                "taxes_id": False,
                "available_in_pos": True,
            }
        )
        amount = 10
        order = self.env["pos.order"].create(
            {
                "session_id": session.id,
                "lines": [
                    (
                        0,
                        0,
                        {
                            "name": "OL/0001",
                            "product_id": product.id,
                            "price_unit": amount,
                            "discount": 0,
                            "qty": 1,
                            "price_subtotal": amount,
                            "price_subtotal_incl": amount,
                        },
                    )
                ],
                "amount_total": amount,
                "amount_tax": 0,
                "amount_paid": 0,
                "amount_return": 0,
            }
        )

        payment_method = session.payment_method_ids[0]
        payment_context = {"active_id": order.id, "active_ids": order.ids}
        payment = (
            self.env["pos.make.payment"]
            .with_context(**payment_context)
            .create(
                {
                    "amount": amount,
                    "payment_method_id": payment_method.id,
                }
            )
            .check()
        )

        payment = order.payment_ids[0]
        payment.write(vals)
        return payment

    def prepare(self):
        # Because this test runs in point_of_sale we can't be sure that pos_mercury is installed.
        if not module_installed(self.env.cr, "pos_mercury"):
            return {}

        payment_method = self.env["pos.payment.method"].create(
            {
                "name": "Mercury test payment method",
            }
        )
        config = self.env["pos.config"].create(
            {
                "name": "Mercury test config",
                "payment_method_ids": [(6, 0, payment_method.ids)],
            }
        )

        with no_fiscal_lock(self.env.cr):
            config.open_ui()

        session = config.current_session_id

        payment_full = self._create_order_with_payment(
            session,
            {
                "ticket": "existing content",
                "mercury_card_number": "3214",
                "mercury_card_brand": "visa",
                "mercury_card_owner_name": "John Smith",
                "mercury_ref_no": "009921",
                "mercury_record_no": "98756541",
                "mercury_invoice_no": "6655442112",
            },
        )

        payment_no_ticket = self._create_order_with_payment(
            session,
            {
                "mercury_card_number": "3214",
                "mercury_card_brand": "visa",
                "mercury_card_owner_name": "John Smith",
                "mercury_ref_no": "009921",
                "mercury_record_no": "98756541",
                "mercury_invoice_no": "6655442112",
            },
        )

        payment_missing_fields = self._create_order_with_payment(
            session,
            {
                "ticket": "existing content",
                "mercury_card_number": "3214",
                "mercury_invoice_no": "6655442112",
            },
        )

        return {
            "pos_payment_full": payment_full.id,
            "pos_payment_no_ticket": payment_no_ticket.id,
            "pos_payment_missing_fields": payment_missing_fields.id,
        }

    def check(self, init):
        # In case pos_mercury was not installed in prepare we won't have anything to test.
        if not init.get("pos_payment_full"):
            return

        self.assertEqual(
            self.env["pos.payment"].browse(init["pos_payment_full"]).ticket,
            "existing content ([Vantiv] card number: 3214, card brand: visa, owner: John Smith, reference: 009921, record: 98756541, invoice: 6655442112)",
        )

        self.assertEqual(
            self.env["pos.payment"].browse(init["pos_payment_no_ticket"]).ticket,
            "([Vantiv] card number: 3214, card brand: visa, owner: John Smith, reference: 009921, record: 98756541, invoice: 6655442112)",
        )

        self.assertEqual(
            self.env["pos.payment"].browse(init["pos_payment_missing_fields"]).ticket,
            "existing content ([Vantiv] card number: 3214, card brand: N/A, owner: N/A, reference: N/A, record: N/A, invoice: 6655442112)",
        )
