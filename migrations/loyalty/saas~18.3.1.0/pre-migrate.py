from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "loyalty.reward", "tax_ids")
