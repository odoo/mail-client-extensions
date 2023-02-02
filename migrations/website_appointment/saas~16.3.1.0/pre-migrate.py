# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "website_appointment.appointment_staff_users_description",
        "website_appointment.appointment_booking_resource_description",
    )
