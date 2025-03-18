from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.workorder", "has_operation_note")
    util.remove_field(cr, "quality.point", "source_document")
    util.remove_field(cr, "quality.point", "worksheet_page")
    util.remove_field(cr, "quality.point", "worksheet_url")
    util.remove_field(cr, "quality.check", "worksheet_url")
    util.remove_field(cr, "quality.check", "worksheet_page")
    util.remove_field(cr, "quality.check", "source_document")
    util.remove_field(cr, "stock.move", "worksheet_note")
    util.remove_view(cr, "mrp_workorder.view_stock_move_operations_quality_check")
