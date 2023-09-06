# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.5")
class Test_00_Simple_SaleSubscriptionPlan_Upgrade(UpgradeCase):
    def prepare(self):
        partner = self.env["res.partner"].create({"name": "Test", "email": "test@opoo.com"})
        recurring_product = self.env["product.template"].create(
            {
                "name": "Recurring Product",
                "recurring_invoice": True,
            }
        )

        # Recurrences
        recurrence_monthly = self.env["sale.temporal.recurrence"].create(
            {
                "duration": 1,
                "unit": "month",
            }
        )

        recurrence_6_month = self.env["sale.temporal.recurrence"].create(
            {
                "duration": 6,
                "unit": "month",
            }
        )

        recurrence_yearly = self.env["sale.temporal.recurrence"].create(
            {
                "duration": 1,
                "unit": "year",
            }
        )

        # Pricing
        self.env["product.pricing"].create(
            [
                {
                    "product_template_id": recurring_product.id,
                    "recurrence_id": recurrence_monthly.id,
                    "price": 10,
                },
                {
                    "product_template_id": recurring_product.id,
                    "recurrence_id": recurrence_6_month.id,
                    "price": 60,
                },
                {
                    "product_template_id": recurring_product.id,
                    "recurrence_id": recurrence_yearly.id,
                    "price": 120,
                },
            ]
        )

        # Template
        template_monthly = self.env["sale.order.template"].create(
            {"name": "Monthly", "recurrence_id": recurrence_monthly.id}
        )

        template_6_month_A = self.env["sale.order.template"].create(
            {
                "name": "6 Month A",
                "recurrence_id": recurrence_6_month.id,
                "user_closable": True,
                "auto_close_limit": 21,
            }
        )

        template_6_month_B = self.env["sale.order.template"].create(
            {
                "name": "6 Month B",
                "recurrence_id": recurrence_6_month.id,
                "user_closable": False,
            }
        )

        # Sale orders
        so = self.env["sale.order"].create(
            [
                {
                    "name": "1 Monthly - no SOT",
                    "recurrence_id": recurrence_monthly.id,
                    "partner_id": partner.id,
                },
                {
                    "name": "2 Monthly - SOT",
                    "sale_order_template_id": template_monthly.id,
                    "recurrence_id": recurrence_monthly.id,
                    "partner_id": partner.id,
                },
                {
                    "name": "3 6 Month - SOT A",
                    "sale_order_template_id": template_6_month_A.id,
                    "partner_id": partner.id,
                },
                {
                    "name": "4 6 Month - SOT B",
                    "sale_order_template_id": template_6_month_B.id,
                    "recurrence_id": recurrence_6_month.id,
                    "partner_id": partner.id,
                },
                {
                    "name": "5 Monthly - SOT A",
                    "sale_order_template_id": template_6_month_A.id,
                    "recurrence_id": recurrence_monthly.id,
                    "partner_id": partner.id,
                },
                {
                    "name": "6 Monthly - SOT A bis",
                    "sale_order_template_id": template_6_month_A.id,
                    "recurrence_id": recurrence_monthly.id,
                    "partner_id": partner.id,
                },
                {
                    "name": "7 Yearly - no SOT",
                    "recurrence_id": recurrence_yearly.id,
                    "partner_id": partner.id,
                },
            ]
        )

        return {"subscriptions_ids": so.ids, "recurring_product_ids": recurring_product.ids}

    def check(self, check):
        so = self.env["sale.order"].browse(check["subscriptions_ids"]).sorted("name")

        self.assertEqual(
            so.mapped("name"),
            [
                "1 Monthly - no SOT",
                "2 Monthly - SOT",
                "3 6 Month - SOT A",
                "4 6 Month - SOT B",
                "5 Monthly - SOT A",
                "6 Monthly - SOT A bis",
                "7 Yearly - no SOT",
            ],
            "Sale order are not correctly ordered",
        )

        plan_ids = [s.plan_id for s in so]
        self.assertEqual(
            [(p.billing_period_value, p.billing_period_unit) for p in plan_ids],
            [(1, "month"), (1, "month"), (6, "month"), (6, "month"), (1, "month"), (1, "month"), (1, "year")],
            "Billing period are not upgraded correctly",
        )

        self.assertEqual(
            [(p.user_closable, p.auto_close_limit) for p in plan_ids],
            [(False, 15), (False, 15), (True, 21), (False, 15), (True, 21), (True, 21), (False, 15)],
            "Billing period are not upgraded correctly",
        )

        price_per_unit = {"year": 120, "month": 10}
        for plan_id in plan_ids:
            self.assertEqual(len(plan_id.product_subscription_pricing_ids), 1, "There should be one pricing per plan")
            self.assertEqual(
                plan_id.product_subscription_pricing_ids.price,
                plan_id.billing_period_value * price_per_unit[plan_id.billing_period_unit],
            )
