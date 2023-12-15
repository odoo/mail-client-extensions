# -*- coding: utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta

try:
    from odoo import Command
except ImportError:
    Command = None

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.2")
class TestAmountToInvoice(UpgradeCase):
    def prepare(self):
        price = 500.0
        downpayment_amount = 100.0

        # As a lock date is set to 15 days from today in another test
        invoice_date = date.today() + relativedelta(months=1)

        customer = self.env["res.partner"].create({"name": "Customer"})

        product = self.env["product.template"].create(
            {
                "name": "Product",
                "taxes_id": False,
            }
        )

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
        downpayment.create_invoices()

        invoice = sale_order.invoice_ids
        invoice.write({"invoice_date": invoice_date})
        invoice.action_post()

        return sale_order.id

    def check(self, sale_order_id):
        sale_order = self.env["sale.order"].browse(sale_order_id)

        self.assertEqual(sale_order.amount_to_invoice, 400.0)
