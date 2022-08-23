# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_attendance.view_attendance_tree_inherit")
    util.remove_view(cr, "hr_attendance.hr_attendance_view_form_inherit")
