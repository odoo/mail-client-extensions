from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.remove_field(cr, "appointment.type", "appointment_count_report")

    renames = [
        "appointment.appointment_type_rule_user_{,write_}unlink",
        "appointment.appointment_invite_rule_user{,_internal}",
        "appointment.appointment_invite_rule_user_{,internal_write_}unlink",
        "appointment.appointment_slot_rule_user_{,write_}unlink",
    ]
    for rename in renames:
        util.rename_xmlid(cr, *eb(rename))

    util.remove_menus(cr, [util.ref(cr, "appointment.menu_schedule_report_all")])
