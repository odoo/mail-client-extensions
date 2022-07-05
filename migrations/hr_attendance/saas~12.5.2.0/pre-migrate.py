# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "last_check_in", "timestamp without time zone")
    util.create_column(cr, "hr_employee", "last_check_out", "timestamp without time zone")
    cr.execute(
        """
        UPDATE hr_employee e
           SET last_check_in = a.check_in,
               last_check_out = a.check_out
          FROM hr_attendance a
         WHERE a.id = e.last_attendance_id
    """
    )

    util.remove_view(cr, "hr_attendance.view_employee_filter_inherit_hr_attendance")
    util.remove_view(cr, "hr_attendance.view_employee_kanban_inherit_hr_attendance")
