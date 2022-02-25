# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    table = "appointment_type" if util.version_gte("saas~15.3") else "calendar_appointment_type"
    util.create_column(cr, table, "work_hours_activated", "boolean", default=True)
