from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.workorder", "measure")
    util.remove_field(cr, "mrp.workorder", "measure_success")
    util.remove_field(cr, "mrp.workorder", "norm_unit")

    util.remove_view(cr, "quality_mrp_workorder.mrp_workorder_view_form_tablet_inherit_quality")
    util.remove_view(cr, "quality_mrp_workorder.mrp_workorder_tablet_view_form_inherit_maintenance")
