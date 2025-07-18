from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "mrp_subcontracting_dropshipping.route_subcontracting_dropshipping")
