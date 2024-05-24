from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "website_appointment_account_payment"):
        util.rename_xmlid(
            cr,
            "website_appointment_account_payment.appointment_progress_bar",
            "appointment_account_payment.appointment_progress_bar",
        )
    util.change_field_selection_values(cr, "product.template", "type", {"booking_fees": "service"})
