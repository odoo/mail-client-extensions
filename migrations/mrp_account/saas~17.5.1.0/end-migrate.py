from odoo.upgrade import util


def migrate(cr, version):
    # these fields are used in project_mrp scripts
    util.remove_field(cr, "mrp.bom", "analytic_distribution_text")
    util.remove_field(cr, "mrp.production", "analytic_distribution")
