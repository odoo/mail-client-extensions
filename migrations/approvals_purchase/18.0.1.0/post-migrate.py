from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "approval.product.line", ["seller_id"])
