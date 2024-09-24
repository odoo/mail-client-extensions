from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_holidays_attendance.holiday_status_extra_hours", util.update_record_from_xml)
