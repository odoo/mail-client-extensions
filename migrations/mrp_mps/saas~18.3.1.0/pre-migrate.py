from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.production.schedule", "enable_max_replenish")
    util.remove_field(cr, "mrp.production.schedule", "max_to_replenish_qty")
