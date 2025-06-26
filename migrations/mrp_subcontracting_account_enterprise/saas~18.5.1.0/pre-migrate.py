from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_subcontracting_account_enterprise.mrp_cost_structure_subcontracting")
