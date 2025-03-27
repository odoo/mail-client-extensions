from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    # the module pos_restaurant_appointment was renamed to pos_appointment
    # but there is still a "new" module named pos_restaurant_appointment that's autoinstalled
    # thus the check for module installed below is "redundant" unless the UPG_AUTOINSTALL
    # env variable is set
    if util.module_installed(cr, "pos_restaurant_appointment"):
        util.rename_xmlid(cr, *eb("pos_{,restaurant_}appointment.view_restaurant_floor_form"))
        util.rename_xmlid(cr, *eb("pos_{,restaurant_}appointment.view_restaurant_table_form"))
    else:
        util.remove_view(cr, "pos_appointment.view_restaurant_floor_form")
        util.remove_view(cr, "pos_appointment.view_restaurant_floor_form")

    util.rename_xmlid(
        cr, *eb("pos_appointment.calendar_event_view_gantt_booking_resource_inherited_{restaurant,pos}_appointment")
    )
    util.rename_xmlid(
        cr, *eb("pos_appointment.calendar_event_view_form_gantt_booking_inherited_{restaurant,pos}_appointment")
    )
