from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "mrp_workorder", "product_uom_id")
    util.rename_field(cr, "mrp.workcenter", "workorder_pending_count", "workorder_blocked_count")
    util.change_field_selection_values(cr, "mrp.workorder", "state", {"pending": "blocked", "waiting": "blocked"})
