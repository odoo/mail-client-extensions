# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'hr.attendance', 'name', 'check_in')
    util.create_column(cr, 'hr_attendance', 'check_out', 'timestamp without time zone')

    cr.execute("""
        UPDATE hr_attendance a
           SET check_out = (SELECT min(b.check_in)
                              FROM hr_attendance b
                             WHERE b.employee_id = a.employee_id
                               AND b.action = 'sign_out'
                               AND b.check_in > a.check_in
                            )
         WHERE a.action = 'sign_in'
    """)
    cr.execute("DELETE FROM hr_attendance WHERE action != 'sign_in'")
    cr.execute("""
        UPDATE hr_attendance
           SET worked_hours = date_part('hour', check_out - check_in) +
                              round(date_part('minute', check_out - check_in)::numeric/60, 2)
         WHERE check_out IS NOT NULL
    """)
    util.remove_field(cr, 'hr.attendance', 'action')
    # sanity checks
    cr.execute("""
        SELECT 'multiple non-check_out: ' || string_agg(id::text, ', ')
          FROM hr_attendance
         WHERE check_out IS NULL
      GROUP BY employee_id
        HAVING count(id) > 1
     UNION ALL
        SELECT 'check_out < check_in: ' || id
          FROM hr_attendance
         WHERE check_out IS NOT NULL
           AND check_out < check_in
     UNION ALL
        SELECT id || ' overlaps with ' || array_to_string(o, ', ')
          FROM (SELECT a.id, array_agg(b.id order by b.id) as o
                  FROM hr_attendance a, hr_attendance b
                 WHERE a.employee_id = b.employee_id
                   AND b.check_out IS NOT NULL
                   AND a.check_in > b.check_in AND a.check_in < b.check_out
              GROUP BY a.id
          ) x
         WHERE array_length(o, 1) > 1 and id = o[1]
    """)
    if cr.rowcount:
        errors = '\n'.join(x[0] for x in cr.fetchall())
        raise util.MigrationError('something goes wrong with attendances:\n' + errors)

    util.remove_field(cr, 'hr.attendance', 'action_desc')
    util.delete_model(cr, 'hr.action.reason')

    util.delete_model(cr, 'report.hr_attendance.report_attendanceerrors')
    view_list = util.splitlines("""
        report_attendanceerrors
        view_attendance_who
        view_attendance_form
    """)
    for view in view_list:
        util.remove_view(cr, "hr_attendance." + view)
    util.rename_xmlid(cr, 'hr_attendance.view_hr_attendance_filter', 'hr_attendance.hr_attendance_view_filter')
