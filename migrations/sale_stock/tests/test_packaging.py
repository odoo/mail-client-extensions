from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.4")
class TestPackaging(UpgradeCase):
    def prepare(self):

        sol = self.env.ref("sale.sale_order_line_3", raise_if_not_found=False)
        if not sol:
            # no demo data? skip test ¯\_(ツ)_/¯
            return None

        box = self.env["product.packaging"].create(
            {
                "name": "box",
                "product_id": sol.product_id.id,
            }
        )

        sol.product_packaging = box.id

        return sol.id

    def check(self, data):
        if not data:
            return
        sol = self.env["sale.order.line"].browse(data)
        assert sol.exists()
        assert sol.product_packaging_qty
