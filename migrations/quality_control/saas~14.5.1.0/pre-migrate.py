# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "quality_control.quality_check_view_form_small")
    util.remove_view(cr, "quality_control.quality_check_view_form_failure")
    util.remove_record(cr, "quality_control.quality_check_action_small")

    # New fields in Quality Point
    util.create_column(cr, "quality_point", "measure_on", "varchar", default="operation")
    util.create_column(cr, "quality_point", "is_lot_tested_fractionally", "bool", default=False)
    util.create_column(cr, "quality_point", "testing_percentage_within_lot", "float8", default=0.0)

    # New fields in Quality Check
    util.create_column(cr, "quality_check", "measure_on", "varchar", default="operation")
    util.create_column(cr, "quality_check", "qty_tested", "float8", default=0.0)
    util.create_column(cr, "quality_check", "move_line_id", "int4")
    util.create_column(cr, "quality_check", "lot_name", "varchar")
    util.create_column(cr, "quality_check", "lot_line_id", "int4")
