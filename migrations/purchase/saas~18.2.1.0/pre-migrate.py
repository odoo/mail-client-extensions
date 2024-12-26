from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "purchase.order.line", "taxes_id", "tax_ids")
