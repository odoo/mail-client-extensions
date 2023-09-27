from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "quality_control_worksheet.view_quality_check_wizard_inherit_worksheet")
    util.remove_view(cr, "quality_control_worksheet.quality_check_view_form_failure_worksheet")
