from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_subcontracting.report_mrp_bom_line_inherit_mrp_subcontracting")
