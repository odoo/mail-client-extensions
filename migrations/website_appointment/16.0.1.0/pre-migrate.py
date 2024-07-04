from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_appointment.user_navbar_inherit_website_enterprise_inherit_website_appointment")
    util.remove_view(cr, "website_appointment.appointments_search_box")
    util.rename_xmlid(
        cr,
        "website_appointment.appointment_type_action_add",
        "website_appointment.appointment_type_action_add_simplified",
    )
    cr.execute(
        """
        UPDATE ir_ui_view
           SET customize_show = FALSE
         WHERE id = %s
        """,
        [util.ref(cr, "website_appointment.opt_appointments_list_cards")],
    )
