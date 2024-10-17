from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "mrp_subcontracting.uom_subcontracting_rule")
