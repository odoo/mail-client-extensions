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
    cr.execute("SELECT id FROM res_company")
    all_companies = [cid for (cid,) in cr.fetchall()]
    cr.execute(
        """
        SELECT t.id
          FROM timer_timer t
          JOIN hr_employee h
         USING (user_id)
         WHERE t.res_model='helpdesk.ticket'
           AND h.active = true
         """
    )
    timer_ids = [tid for (tid,) in cr.fetchall()]
    if timer_ids:
        timesheet_vals_list = []
        minimum_duration = max(0, int(env["ir.config_parameter"].get_param("timesheet_grid.timesheet_min_duration", 0)))
        rounding = max(1, int(env["ir.config_parameter"].get_param("timesheet_grid.timesheet_rounding", 1)))

        for t in util.iter_browse(env["timer.timer"], timer_ids):
            ticket = env["helpdesk.ticket"].browse(t.res_id).exists()
            if not ticket.project_id.account_id.active or not t.user_id.employee_ids:
                continue
            if ticket.project_id.company_id and not any(
                e.company_id.id == ticket.project_id.company_id.id for e in t.user_id.employee_ids
            ):
                continue
            company_id = (
                ticket.company_id.id or ticket.project_id.company_id.id or t.user_id.employee_ids[0].company_id.id
            )
            minutes_spent = t._get_minutes_spent()
            timesheet_vals_list.append(
                {
                    "helpdesk_ticket_id": ticket.id,
                    "project_id": ticket.project_id.id,
                    "account_id": ticket.project_id.account_id.id,
                    "date": t.timer_start.date(),
                    "name": "/",
                    "user_id": t.user_id.id,
                    "company_id": company_id,
                    "unit_amount": round_time_spent(minutes_spent, minimum_duration, rounding) / 60,
                }
            )
        AAL = env["account.analytic.line"].with_context(allowed_company_ids=all_companies)
        if timesheet_vals_list:
            util.iter_browse(AAL, []).create(timesheet_vals_list)
        util.iter_browse(env["timer.timer"], timer_ids).unlink()
