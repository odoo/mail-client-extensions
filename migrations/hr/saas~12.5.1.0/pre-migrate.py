# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.employee", "google_drive_link")
    util.remove_field(cr, "res.users", "google_drive_link")

    # This field was defined as stored in `hr_presence` module.
    # It moved as a computed field in `hr`.
    # A new `hr_presence_state_display` stored field has been added in `hr_presence` module which
    # contains the same value and is used to allow group_by in kanban view
    util.move_field_to_module(cr, "hr.employee", "hr_presence_state", "hr_presence", "hr")
    if util.column_exists(cr, "hr_employee", "hr_presence_state"):
        cr.execute("ALTER TABLE hr_employee RENAME COLUMN hr_presence_state TO hr_presence_state_display")

    util.move_field_to_module(cr, "hr.employee", "last_activity", "hr_presence", "hr")

    if util.table_exists(cr, "hr_plan_activity_type"):
        util.create_column(cr, "hr_plan_activity_type", "note", "text")

    # NOTE: do no move `res.config.settings` related, they are in both module
    util.create_column(cr, "res_company", "hr_presence_control_email_amount", "int4")
    util.move_field_to_module(cr, "res.company", "hr_presence_control_email_amount", "hr_presence", "hr")
    util.create_column(cr, "res_company", "hr_presence_control_ip_list", "varchar")
    util.move_field_to_module(cr, "res.company", "hr_presence_control_ip_list", "hr_presence", "hr")

    util.remove_column(cr, "res_users", "employee_id")  # not stored anymore

    util.remove_record(cr, "hr.hr_employee_action_subordinate_hierachy")  # yes, with the typo
    util.remove_record(cr, "hr.hr_employee_action_toggle_active")
    util.remove_view(cr, "hr.res_users_view_form_profile")
