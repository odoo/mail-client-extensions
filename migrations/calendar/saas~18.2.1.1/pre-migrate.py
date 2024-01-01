from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "calendar_sms"):
        util.move_field_to_module(cr, "calendar.alarm", "sms_notify_responsible", "calendar_sms", "calendar")
        util.rename_field(cr, "calendar.alarm", "sms_notify_responsible", "notify_responsible")
