# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "appointment.calendar_alarm_data_1h_sms", "appointment_sms.calendar_alarm_data_1h_sms")
