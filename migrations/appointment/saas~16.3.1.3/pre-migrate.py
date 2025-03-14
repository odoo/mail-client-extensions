from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.change_field_selection_values(
        cr,
        "appointment.type",
        "assign_method",
        {"chosen": "resource_time", "random": "time_auto_assign"},
    )
    util.rename_field(cr, "appointment.invite", "staff_users_choice", "resources_choice")
    util.change_field_selection_values(
        cr,
        "appointment.invite",
        "resources_choice",
        {"all_assigned_users": "all_assigned_resources", "specific_users": "specific_resources"},
    )
    util.create_column(cr, "appointment_type", "schedule_based_on", "varchar", default="users")
    # Avoid running the compute method on all appointment types as the existing ones will be False anyway
    util.create_column(cr, "appointment_type", "resource_manage_capacity", "boolean", default=False)

    # Rename of xmlid
    renames = [
        "appointment.calendar_event_view_form{_inherit_appointment,}",
        "appointment.calendar_event_view_tree{_inherit_appointment,}",
        "appointment.calendar_event_view_search{_inherit_appointment,}",
    ]
    for rename in renames:
        util.rename_xmlid(cr, *eb(rename))
