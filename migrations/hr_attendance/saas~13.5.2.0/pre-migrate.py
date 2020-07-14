# -*- coding: utf-8 -*-
from odoo.upgrade import util

def migrate(cr, version):
    util.remove_menus(cr, [util.ref(cr, "hr_attendance.menu_hr_attendance_kiosk_mode")])
