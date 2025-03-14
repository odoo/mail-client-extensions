from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(
        cr, "quality_mrp_workorder_worksheet.mrp_workorder_view_form_tablet_inherit_quality_control_worksheet"
    )
