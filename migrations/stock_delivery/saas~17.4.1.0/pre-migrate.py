from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking", "package_ids")
