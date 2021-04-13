# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.5")
class TestWebsiteSaleStock(UpgradeCase):
    def prepare(self):
        product_available = self.env["product.product"].create(
            {
                "name": "Product A",
                "inventory_availability": "never",
                "type": "product",
                "default_code": "TEST_WSS_AVAILABLE",
            }
        )
        product_out_of_stock = self.env["product.product"].create(
            {
                "name": "Product B",
                "inventory_availability": "always",
                "type": "product",
                "default_code": "TEST_WSS_OUT_OF_STOCK",
            }
        )
        return {"product_out_of_stock_id": product_out_of_stock.id, "product_available_id": product_available.id}

    def check(self, init):
        product_available = self.env["product.product"].browse(init["product_available_id"])
        self.assertEqual(product_available.allow_out_of_stock_order, True)
        product_out_of_stock = self.env["product.product"].browse(init["product_out_of_stock_id"])
        self.assertEqual(product_out_of_stock.allow_out_of_stock_order, False)
