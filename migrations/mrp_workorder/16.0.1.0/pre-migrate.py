from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.workorder", "skipped_check_ids")
    util.remove_field(cr, "mrp.workorder", "component_id")
    util.remove_field(cr, "mrp.workorder", "component_tracking")
    util.remove_field(cr, "mrp.workorder", "component_remaining_qty")
    util.remove_field(cr, "mrp.workorder", "component_uom_id")
    util.remove_field(cr, "mrp.workorder", "control_date")
    util.remove_field(cr, "mrp.workorder", "is_first_step")
    util.remove_field(cr, "mrp.workorder", "is_last_step")
    util.remove_field(cr, "mrp.workorder", "note")
    util.remove_field(cr, "mrp.workorder", "skip_completed_checks")
    util.remove_field(cr, "mrp.workorder", "component_qty_to_do")
    util.remove_field(cr, "quality.point", "worksheet")
    util.remove_field(cr, "quality.check", "quality_state_for_summary")

    util.remove_view(cr, "mrp_workorder.mrp_workorder_view_form_tablet_menu")
