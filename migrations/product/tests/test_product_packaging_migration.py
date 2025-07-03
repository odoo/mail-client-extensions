from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.1")
class TestProductPackagingMigration(UpgradeCase):
    def prepare(self):
        dummy_category = self.env["uom.category"].create(
            {
                "name": "Test Category",
            }
        )
        test_uom = self.env["uom.uom"].create(
            {
                "name": "Test Unit",
                "category_id": dummy_category.id,
                "uom_type": "reference",
            }
        )
        product_a, product_b, product_c, product_d, product_e = self.env["product.product"].create(
            [
                {
                    "name": name,
                    "type": "consu",
                    "uom_id": test_uom.id,
                }
                for name in ["Product A", "Product B", "Product C", "Product D", "Product E"]
            ]
        )
        packaging_1_vals = {
            "qty": 6,
            "name": "Test Pack of 6",
        }
        sale_installed = util.module_installed(self.env.cr, "sale")
        if sale_installed:
            packaging_1_vals["sales"] = True
        self.env["product.packaging"].create(
            [
                {
                    "product_id": product.id,
                    "barcode": barcode,
                    **packaging_1_vals,
                }
                for product, barcode in zip([product_a, product_b], ["test_barcode_a", "test_barcode_b"])
            ]
        )
        packaging_2_vals = {
            "qty": 6,
            "name": "Test 6 Pack",
            "barcode": "test_barcode_c",
        }
        if sale_installed:
            packaging_2_vals["sales"] = True
        self.env["product.packaging"].create(
            {
                "product_id": product_c.id,
                **packaging_2_vals,
            }
        )
        packaging_3_vals = {
            "qty": 10,
            "name": "Test Pack of 10",
            "barcode": "test_barcode_d",
        }
        if sale_installed:
            packaging_3_vals["sales"] = True
        self.env["product.packaging"].create(
            {
                "product_id": product_d.id,
                **packaging_3_vals,
            }
        )
        packaging_4_vals = {
            "qty": 10,
            "name": "Test Box of 10",
            "barcode": "test_barcode_e",
        }
        if sale_installed:
            packaging_4_vals["sales"] = False
        self.env["product.packaging"].create(
            {
                "product_id": product_e.id,
                **packaging_4_vals,
            }
        )
        return product_a.id, product_b.id, product_c.id, product_d.id, product_e.id, sale_installed

    def check(self, init):
        product_a_id, product_b_id, product_c_id, product_d_id, product_e_id, sale_was_installed = init
        product_a, product_b, product_c, product_d, product_e = self.env["product.product"].browse(
            [product_a_id, product_b_id, product_c_id, product_d_id, product_e_id]
        )
        packagings = self.env["uom.uom"].search([("name", "in", ["Test Pack of 6", "Pack 10.00"])])
        self.assertEqual(len(packagings), 2, "Packagings with the same name and quantity should be merged")
        self.assertEqual(set(packagings.mapped("name")), {"Test Pack of 6", "Pack 10.00"})
        self.assertEqual(set(packagings.mapped("relative_factor")), {6, 10})
        self.assertEqual(
            product_a.uom_ids,
            packagings.filtered(lambda p: p.relative_factor == 6 and p.name == "Test Pack of 6")
            if sale_was_installed
            else self.env["uom.uom"],
        )
        self.assertEqual(product_a.uom_ids, product_b.uom_ids)
        self.assertEqual(product_a.uom_ids, product_c.uom_ids)
        self.assertEqual(
            product_d.uom_ids,
            packagings.filtered(lambda p: p.relative_factor == 10 and p.name == "Pack 10.00")
            if sale_was_installed
            else self.env["uom.uom"],
        )
        self.assertEqual(product_e.uom_ids, self.env["uom.uom"])
        self.assertEqual(product_a.product_uom_ids.barcode, "test_barcode_a", "Barcode is not correctly set")
        self.assertEqual(product_b.product_uom_ids.barcode, "test_barcode_b", "Barcode is not correctly set")
        self.assertEqual(product_c.product_uom_ids.barcode, "test_barcode_c", "Barcode is not correctly set")
        self.assertEqual(product_d.product_uom_ids.barcode, "test_barcode_d", "Barcode is not correctly set")
        self.assertEqual(product_e.product_uom_ids.barcode, "test_barcode_e", "Barcode is not correctly set")
