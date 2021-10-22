# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "appointment_type_res_users_rel", "calendar_appointment_type", "res_users")

    # Field employee_ids (hr.employee) is replaced with staff_user_ids (res.users) on calendar.apointment.type
    # We fill the new table with users corresponding to the existing employees, then remove the table.
    cr.execute(
        """
       INSERT INTO appointment_type_res_users_rel(calendar_appointment_type_id, res_users_id)
            SELECT wct.calendar_appointment_type_id, emp.user_id
              FROM appointment_type_employee_rel wct
              JOIN hr_employee emp ON wct.hr_employee_id = emp.id
             WHERE emp.user_id IS NOT NULL
        """
    )
    cr.execute("DROP TABLE appointment_type_employee_rel")
    util.remove_field(cr, "calendar.appointment.type", "employee_ids")

    util.remove_field(cr, "calendar.appointment.share", "suggested_employee_ids")
    util.remove_field(cr, "calendar.appointment.share", "employee_ids")
    util.rename_xmlid(cr, "appointment.employee_select", "appointment.staff_user_select")
    util.remove_view(cr, "appointment.appointment_select_timezone")
