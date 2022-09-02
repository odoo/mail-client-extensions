from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    env["res.company"]._create_missing_subcontracting_dropshipping_sequence()
    env["res.company"]._create_missing_subcontracting_dropshipping_picking_type()
