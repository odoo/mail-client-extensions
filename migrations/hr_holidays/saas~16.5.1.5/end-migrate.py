from odoo.tools import float_compare, float_round

from odoo.upgrade import util


def migrate(cr, version):
    # recompute `number_of_hours` without recomputing `number_of_days`, that can have been changed by the user.
    cr.execute("""
       SELECT id
         FROM hr_leave
        WHERE date_from IS NOT NULL
          AND date_to IS NOT NULL
          AND resource_calendar_id IS NOT NULL
    """)
    ids = [r[0] for r in cr.fetchall()]
    Leave = util.env(cr)["hr.leave"].with_context(mail_notrack=True)
    for leave in util.iter_browse(Leave, ids):
        days, hours = leave._get_duration(check_leave_type=False)

        ratio = (
            # keep hours if the leave was less than one day
            1
            if not days
            # if there is a mismatch in hours-per-day with the value in
            # the calendar, use the computed days
            else days
            if float_compare(leave.resource_calendar_id.hours_per_day, hours / days, precision_digits=2) != 0
            # when hours-per-day match, account for a possible mismatch with the
            # number of days in the leave
            else (leave.number_of_days / days)
        )
        leave.number_of_hours = float_round(hours * ratio, precision_digits=2)
