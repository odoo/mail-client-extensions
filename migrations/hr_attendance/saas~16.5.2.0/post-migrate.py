from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """SELECT att.id, ot.duration
                  FROM hr_attendance att
                  INNER JOIN hr_attendance_overtime ot
                        ON date_trunc('day',att.check_in) = date_trunc('day', ot.date)
                        AND date_trunc('day',att.check_out) = date_trunc('day', ot.date)
                        AND att.employee_id = ot.employee_id
                  WHERE ot.duration > 0
                  """
    )
    to_compute_ids = [row[0] for row in cr.fetchall()]
    util.recompute_fields(cr, "hr.attendance", ["overtime_hours"], ids=to_compute_ids)
