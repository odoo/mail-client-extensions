from odoo import models

from odoo.upgrade import util


class Uom(models.Model):
    _name = "uom.uom"
    _inherit = "uom.uom"
    _module = "approvals_purchase"

    def _compute_quantity(self, *args, **kwargs):
        if self.env.context.get("upg_seller_id_recompute_flag"):
            kwargs = dict(kwargs, raise_if_failure=False)
        return super()._compute_quantity(*args, **kwargs)


def migrate(cr, version):
    util.create_column(
        cr, "approval_product_line", "seller_id", "int4", fk_table="product_supplierinfo", on_delete_action="SET NULL"
    )
