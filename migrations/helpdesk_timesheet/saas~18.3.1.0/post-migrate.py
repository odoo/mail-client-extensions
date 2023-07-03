from odoo.addons.timer.utils.timer_utils import round_time_spent

from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    # if some timers linked to a ticket exist then we have to generate
    # a timesheet since after the migration a timesheet will be generated
    # when a timer will start in ticket. After that, the timer will be automatically stopped
    # because a existing timer could be existed in timesheet for a same user
    # and so to be sure only one timer in same model for a same user exists
    # those existing timers will be stopped.
    cr.execute("SELECT id FROM timer_timer WHERE res_model='helpdesk.ticket'")
    timer_ids = [tid for (tid,) in cr.fetchall()]
    if timer_ids:
        timesheet_vals_list = []
        minimum_duration = max(0, int(env["ir.config_parameter"].get_param("timesheet_grid.timesheet_min_duration", 0)))
        rounding = max(1, int(env["ir.config_parameter"].get_param("timesheet_grid.timesheet_rounding", 1)))

        for t in util.iter_browse(env["timer.timer"], timer_ids):
            ticket = env["helpdesk.ticket"].browse(t.res_id)
            minutes_spent = t._get_minutes_spent()
            timesheet_vals_list.append(
                {
                    "helpdesk_ticket_id": ticket.id,
                    "project_id": ticket.project_id.id,
                    "date": t.timer_start.date(),
                    "name": "/",
                    "user_id": t.user_id.id,
                    "unit_amount": round_time_spent(minutes_spent, minimum_duration, rounding) / 60,
                }
            )
        util.iter_browse(env["account.analytic.line"], []).create(timesheet_vals_list)
        util.iter_browse(env["timer.timer"], timer_ids).unlink()
