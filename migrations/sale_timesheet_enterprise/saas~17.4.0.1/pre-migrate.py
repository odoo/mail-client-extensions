from odoo.addons.resource.models.utils import HOURS_PER_DAY

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "billing_rate_target", "float8")
    cr.execute(
        """
           UPDATE hr_employee he
              SET billing_rate_target = (he.billable_time_target * (comp.billing_rate_target / 100.0)) / (COALESCE(cal.hours_per_day, %s) * 20.0)
             FROM res_company comp
        LEFT JOIN resource_calendar cal
               ON comp.resource_calendar_id = cal.id
            WHERE he.company_id = comp.id
              AND he.billable_time_target > 0
              AND comp.billing_rate_target > 0
        """,
        [HOURS_PER_DAY],
    )
    util.remove_field(cr, "res.company", "billing_rate_target")
    util.remove_constraint(cr, "res_company", "res_company_check_billing_rate")
    util.remove_field(cr, "res.config.settings", "billing_rate_target")
    util.remove_field(cr, "hr.employee", "billable_time_target")
    util.remove_constraint(cr, "hr_employee", "hr_employee_check_billable_time_target")
    util.rename_field(cr, "hr.employee", "show_billable_time_target", "show_billing_rate_target")
