from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_attendance.open_kiosk_url")
    util.remove_menus(cr, [util.ref(cr, "hr_attendance.menu_hr_attendance_kiosk_no_user_mode")])
