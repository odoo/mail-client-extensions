from contextlib import ExitStack
from datetime import date
from unittest.mock import patch

from dateutil.relativedelta import relativedelta

try:
    from odoo import Command
except ImportError:
    Command = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import module_installed


@change_version("saas~16.2")
class TestAmountToInvoice(UpgradeCase):
    def prepare(self):
        price = 500.0
        downpayment_amount = 100.0

        # As a lock date is set to 15 days from today in another test
        invoice_date = date.today() + relativedelta(months=1)

        customer = self.env["res.partner"].create({"name": "Customer"})

        product = self.env["product.product"].create(
            {
                "name": "Product",
                "taxes_id": False,
            }
        )
        journal_data = {
            "name": "TestAmountToInvoice[16.2]",
            "code": "TATI",
            "type": "sale",
        }
        if module_installed(self.env.cr, "l10n_latam_invoice_document"):
            journal_data["l10n_latam_use_documents"] = False

        journal = self.env["account.journal"].create(journal_data)

        sale_order = self.env["sale.order"].create(
            {
                "partner_id": customer.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "price_unit": price,
                        }
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        downpayment = self.env["sale.advance.payment.inv"].create(
            {
                "advance_payment_method": "fixed",
                "fixed_amount": downpayment_amount,
                "sale_order_ids": [Command.set(sale_order.ids)],
            }
        )
        downpayment.with_context({"default_journal_id": journal.id}).create_invoices()

        invoice = sale_order.invoice_ids
        invoice.write({"invoice_date": invoice_date})

        with ExitStack() as stack:
            if module_installed(self.env.cr, "l10n_mx_edi"):
                stack.enter_context(
                    patch.object(
                        type(self.env["account.edi.format"]), "_l10n_mx_edi_check_configuration", lambda _, __: []
                    )
                )

            invoice.action_post()

        return sale_order.id

    def check(self, sale_order_id):
        sale_order = self.env["sale.order"].browse(sale_order_id)

        self.assertEqual(sale_order.amount_to_invoice, 400.0)
