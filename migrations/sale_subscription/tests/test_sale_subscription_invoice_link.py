from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo import fields

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("15.3")
class TestSaleOrderSubscriptionInvoiceCount(UpgradeCase):
    def prepare(self):
        uom_category = self.env["uom.category"].create([{"name": "Time"}])
        uom_month = self.env["uom.uom"].create(
            {"name": "Months", "category_id": uom_category.id, "uom_type": "reference"}
        )

        journal_sale = self.env["account.journal"].create(
            {"name": "Sale Journal for subscription", "code": "SALE-SUB", "type": "sale"}
        )
        user_type_income = self.env.ref("account.data_account_type_revenue")
        account_income_id = self.env["account.account"].create(
            {"code": "PC211", "name": "Product Sale", "user_type_id": user_type_income.id}
        )

        user_type_receivable = self.env.ref("account.data_account_type_receivable")
        receivable_account_id = self.env["account.account"].create(
            {
                "code": "TR1",
                "name": "Test Receivable Account",
                "user_type_id": user_type_receivable.id,
                "reconcile": True,
            }
        )
        partner_id = (
            self.env["res.partner"]
            .create(
                {
                    "name": "John Micheal",
                    "email": "j@odoo.com",
                    "property_account_receivable_id": receivable_account_id.id,
                }
            )
            .id
        )
        subscription_template_id = (
            self.env["sale.subscription.template"]
            .create(
                {
                    "name": "Cloud Hosting",
                    "description": "Cloud Hosting 1 - monthly",
                    "recurring_rule_type": "monthly",
                    "recurring_interval": 1,
                    "recurring_rule_boundary": "unlimited",
                    "payment_mode": "draft_invoice",
                    "journal_id": journal_sale.id,
                }
            )
            .id
        )
        product_value = {
            "name": "Odoo Cloud Hosting - Standard Cloud (per month)",
            "list_price": 300,
            "sale_ok": True,
            "recurring_invoice": True,
            "subscription_template_id": subscription_template_id,
            "uom_id": uom_month.id,
            "uom_po_id": uom_month.id,
            "property_account_income_id": account_income_id.id,
        }
        product_template_record = self.env["product.template"].create(product_value)
        product_ids = product_template_record.product_variant_ids.ids
        line_values = [
            (
                0,
                0,
                {
                    "product_id": product_ids[0],
                    "quantity": 1,
                    "price_unit": 300,
                    "uom_id": uom_month.id,
                },
            )
        ]

        sub_without_so = self.env["sale.subscription"]
        with freeze_time("2022-12-01"):
            sub_without_so = self.env["sale.subscription"].create(
                [
                    {
                        "name": "CLOUDHOSTING",
                        "partner_id": partner_id,
                        "template_id": subscription_template_id,
                        "recurring_invoice_line_ids": line_values,
                    }
                ]
            )
            sub_without_so.start_subscription()
        start_date = fields.Date.today()
        moves = self.env["account.move"]
        with freeze_time(start_date - relativedelta(months=1)):
            moves |= self.env["sale.subscription"]._cron_recurring_create_invoice()
        with freeze_time(start_date):
            moves |= self.env["sale.subscription"]._cron_recurring_create_invoice()
        return {"moves": moves.ids, "sub_without_so": sub_without_so.id}

    def check(self, init):
        moves = self.env["account.move"].browse(init["moves"])
        order = moves.mapped("line_ids.sale_line_ids.order_id")
        invoices = order.order_line.invoice_lines.move_id.filtered(
            lambda r: r.move_type in ("out_invoice", "out_refund")
        )
        self.assertEqual(len(order), 1)
        self.assertEqual(len(invoices), 2)
