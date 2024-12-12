from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "quality_check", "workcenter_id")
    util.remove_column(cr, "quality_check", "finished_lot_id")
    util.remove_field(cr, "mrp.workorder", "additional")
    util.remove_field(cr, "mrp.workorder", "qty_done")
    util.remove_field(cr, "mrp.workorder", "move_line_id")
    util.remove_field(cr, "quality.check", "additional")
    util.remove_field(cr, "quality.check", "component_qty_to_do")
    util.remove_field(cr, "quality.check", "component_remaining_qty")
    util.remove_field(cr, "quality.check", "qty_done")
    if util.module_installed(cr, "quality_control"):
        util.move_field_to_module(cr, "quality.check", "move_line_id", "mrp_workorder", "quality_control")
    else:
        util.remove_field(cr, "quality.check", "move_line_id")
    util.remove_field(cr, "stock.move.line", "quality_check_ids")
    util.remove_view(cr, "mrp_workorder.quality_check_view_form_tablet")
