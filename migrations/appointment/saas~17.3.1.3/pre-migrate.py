from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "appointment.type", "user_assign_method")
    util.remove_field(cr, "appointment.manage.leaves", "calendar_id")

    if util.module_installed(cr, "website_appointment"):
        util.rename_xmlid(cr, "website_appointment.appointment_progress_bar", "appointment.appointment_progress_bar")
