from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_workorder.mrp_bom_form_view_inherit")
