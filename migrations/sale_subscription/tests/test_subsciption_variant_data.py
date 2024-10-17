from datetime import datetime, timedelta

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~15.3")
class Test_00_VARIANT_MIGRATION(UpgradeCase):
    def prepare(self):
        product_attribute = self.env["product.attribute"].create(
            {
                "name": "Duration",
                "sequence": 30,
            }
        )

        product_attribute_value_1 = self.env["product.attribute.value"].create(
            {
                "name": "1 year",
                "attribute_id": product_attribute.id,
            }
        )

        product_attribute_value_2 = self.env["product.attribute.value"].create(
            {
                "name": "2 year",
                "attribute_id": product_attribute.id,
            }
        )

        yearly_subscription_template = self.env["sale.subscription.template"].create(
            {
                "name": "Yearly Subscription",
                "code": "YEA",
                "recurring_interval": 1,
                "recurring_rule_type": "yearly",
                "payment_mode": "success_payment",
                "user_closable": True,
            }
        )

        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Public Pricelist",
                "sequence": 1,
            }
        )

        subscription_record = self.env["sale.subscription"].create(
            {
                "name": "Office Cleaning Servicexx",
                "partner_id": self.env.user.partner_id.id,
                "template_id": yearly_subscription_template.id,
                "pricelist_id": pricelist.id,
                "user_id": self.env.user.id,
                "date_start": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "recurring_next_date": (datetime.now() - timedelta(days=1) + timedelta(days=365)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )

        uom_category = self.env["uom.category"].create(
            {
                "name": "Time",
            }
        )

        subscription_uom_year = self.env["uom.uom"].create(
            {
                "name": "Years",
                "category_id": uom_category.id,
                "factor_inv": 1.0,
                "uom_type": "reference",
            }
        )

        product = self.env["product.product"].create(
            {
                "name": "Office Cleaning Subscription (Yearly)xxxx",
                "recurring_invoice": True,
                "subscription_template_id": yearly_subscription_template.id,
                "type": "service",
                "list_price": 2000.0,
                "invoice_policy": "order",
                "uom_id": subscription_uom_year.id,
                "uom_po_id": subscription_uom_year.id,
            }
        )

        product_tmpl_id = product.product_tmpl_id.id
        self.env["product.template.attribute.line"].create(
            {
                "attribute_id": product_attribute.id,
                "product_tmpl_id": product_tmpl_id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            product_attribute_value_1.id,
                            product_attribute_value_2.id,
                        ],
                    )
                ],
            },
        )

        variants = self.env["product.product"].search(
            [
                (
                    "product_tmpl_id",
                    "=",
                    product_tmpl_id,
                )
            ]
        )

        prices = [200.0, 2000.0]
        names = ["SSL1", "SSL2"]
        variant_to_price_mapping = []
        for variant, price, name in zip(variants, prices, names):
            self.env["sale.subscription.line"].create(
                {
                    "analytic_account_id": subscription_record.id,
                    "product_id": variant.id,
                    "name": name,
                    "uom_id": subscription_uom_year.id,
                    "price_unit": price,
                },
            )
            variant_to_price_mapping.append((variant.id, price))

        return {"product_template_id": product_tmpl_id, "variant_to_price_mapping": variant_to_price_mapping}

    def check(self, check):
        product_template_id = check["product_template_id"]
        input_variant_price_map = sorted(check["variant_to_price_mapping"])
        output_variant_price_map = []

        output_variant_price_map = [
            [variant.id, pricing.price]
            for pricing in self.env["product.pricing"].search([("product_template_id", "=", product_template_id)])
            for variant in pricing["product_variant_ids"]
        ]

        output_variant_price_map.sort()
        self.assertEqual(input_variant_price_map, output_variant_price_map, "variant records not migrated properly")
