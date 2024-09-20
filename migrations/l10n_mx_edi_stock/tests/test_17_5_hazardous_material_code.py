from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.5")
class TestHazardousMaterialCodeMigration(UpgradeCase):
    def prepare(self):
        if "l10n_mx_edi_hazardous_material_code" not in self.env["product.product"]:
            # `l10n_mx_edi_stock_extended` not installed - skip test
            return {"l10n_mx_edi_stock_extended_not_installed": True}

        product_code_ok = self.env["product.product"].create(
            {
                "name": "Product with ok hazmat code",
                "type": "consu",
                "list_price": 100.0,
                "standard_price": 50.0,
                "l10n_mx_edi_hazardous_material_code": "0004",
            }
        )
        product_code_bad = self.env["product.product"].create(
            {
                "name": "Product with bad hazmat code",
                "type": "consu",
                "list_price": 100.0,
                "standard_price": 50.0,
                "l10n_mx_edi_hazardous_material_code": "12345",
            }
        )
        return {
            "product_code_ok": product_code_ok.id,
            "product_code_bad": product_code_bad.id,
        }

    def check(self, init):
        if init.get("l10n_mx_edi_stock_extended_not_installed"):
            return

        product_code_ok = self.env["product.product"].browse(init["product_code_ok"])
        product_code_bad = self.env["product.product"].browse(init["product_code_bad"])

        self.assertRecordValues(
            product_code_ok,
            [{"l10n_mx_edi_hazardous_material_code_id": self.env.ref("l10n_mx_edi_stock.hazardous_material_0").id}],
        )

        unknown_hazardous_material = self.env.ref("__upgrade__.l10n_mx_unknown_hazardous_material")
        self.assertRecordValues(
            product_code_bad,
            [{"l10n_mx_edi_hazardous_material_code_id": unknown_hazardous_material.id}],
        )
