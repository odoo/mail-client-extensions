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

        # compute the ratio between the chosen and the guessed number of days
        ratio = leave.number_of_days / days if days else 1
        leave.number_of_hours = round(hours * ratio)
