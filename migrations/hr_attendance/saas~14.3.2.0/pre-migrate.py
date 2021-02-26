# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_attendance.menu_hr_attendance_attendances_overview")
    util.remove_menus(cr, [
        util.ref(cr, "hr_attendance.menu_hr_attendance_view_employees_kanban"),
        util.ref(cr, "hr_attendance.menu_hr_attendance_manage_attendances"),
    ])
