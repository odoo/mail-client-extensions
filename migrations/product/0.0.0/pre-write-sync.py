from odoo.addons.base.maintenance.migrations import util

if util.version_gte("17.0"):
    from odoo import models

    from odoo.addons.product.models import product_product  # noqa

    class ProductProduct(models.Model):
        _name = "product.product"
        _inherit = "product.product"
        _module = "product"

        def _compute_write_date(self):
            # do not update write date to avoid MemoryError, we update in end-
            pass


def migrate(cr, version):
    pass
