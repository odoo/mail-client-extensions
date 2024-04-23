from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "planning.planning", "slot_ids")
    util.remove_model(cr, "slot.planning.select.send")

    util.remove_view(cr, "planning.slot_planning_select_send_view_form")
    util.remove_record(cr, "planning.model_planning_slot_action_publish")

    if not util.module_installed(cr, "sale_planning"):
        util.remove_column(cr, "hr_employee", "default_planning_role_id")
