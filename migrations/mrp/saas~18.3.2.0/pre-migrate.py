from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "mrp_workorder", "product_uom_id")
    util.rename_field(cr, "mrp.workcenter", "workorder_pending_count", "workorder_blocked_count")
    util.change_field_selection_values(cr, "mrp.workorder", "state", {"pending": "blocked", "waiting": "blocked"})
    util.remove_field(cr, "mrp.routing.workcenter", "worksheet_type")
    util.remove_field(cr, "mrp.routing.workcenter", "note")
    util.remove_field(cr, "mrp.routing.workcenter", "worksheet", keep_as_attachments=True)
    util.remove_field(cr, "mrp.routing.workcenter", "worksheet_google_slide")
    util.remove_field(cr, "mrp.workorder", "worksheet")
    util.remove_field(cr, "mrp.workorder", "worksheet_type")
    util.remove_field(cr, "mrp.workorder", "worksheet_google_slide")
    util.remove_field(cr, "mrp.workorder", "operation_note")
