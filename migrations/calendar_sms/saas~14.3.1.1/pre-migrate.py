# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "calendar_alarm", "sms_template_id", "int4")

    reminder_template = util.ref(cr, "calendar_sms.sms_template_data_calendar_reminder")
    if reminder_template:
        cr.execute(
            """
               UPDATE calendar_alarm
                  SET sms_template_id = %s
                WHERE alarm_type='sms'
            """,
            [reminder_template],
        )
