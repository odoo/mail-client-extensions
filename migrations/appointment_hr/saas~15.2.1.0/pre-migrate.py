# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "calendar_appointment_type", "work_hours_activated", "boolean", default=True)
