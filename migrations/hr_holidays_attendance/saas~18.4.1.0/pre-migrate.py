from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE hr_leave_accrual_level
            SET frequency = 'worked_hours'
            FROM hr_leave_accrual_plan
            WHERE frequency_hourly_source = 'attendance'
              AND frequency = 'hourly'
              AND accrued_gain_time = 'end'
        """
    )

    util.remove_field(cr, "hr.leave.accrual.level", "frequency_hourly_source")
