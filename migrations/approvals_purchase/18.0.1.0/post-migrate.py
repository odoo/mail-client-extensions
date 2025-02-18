from odoo.upgrade import util


def migrate(cr, version):
    apl = util.env(cr)["approval.product.line"].with_context(upg_seller_id_recompute_flag=True)
    util.recompute_fields(cr, apl, ["seller_id"])
