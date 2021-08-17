# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "quality_control_worksheet.quality_check_view_form_small_inherit_worksheet")
    util.remove_view(cr, "quality_control_worksheet.quality_check_view_form_failure_inherit_worksheet")
    util.remove_view(cr, "quality_control_worksheet.worksheet_custom")
    util.remove_record(cr, "quality_control_worksheet.quality_check_custom_report")
    util.remove_model(cr, "report.quality_control_worksheet.worksheet_custom")
