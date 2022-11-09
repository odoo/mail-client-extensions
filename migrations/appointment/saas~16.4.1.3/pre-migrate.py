# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "appointment.appointment_onboarding_panel", "appointment.onboarding_onboarding_appointment")
