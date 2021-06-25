# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.employee", "mobile_invoice", "l10n_be_hr_contract_salary", "hr_payroll")
    util.move_field_to_module(cr, "hr.employee", "sim_card", "l10n_be_hr_contract_salary", "hr_payroll")
    util.move_field_to_module(cr, "hr.employee", "internet_invoice", "l10n_be_hr_contract_salary", "hr_payroll")

    util.create_column(cr, "hr_contract", "calendar_changed", "bool", default=False)

    # Populate calendar changed
    # calendar_changed should be true when the previous or the next contract has a different resource_calendar_id
    cr.execute(
        """
        WITH helper AS (SELECT ctr.id,
                               LAG(ctr.id) over (partition by (employee_id) order by (date_start)) AS previous,
                               LEAD(ctr.id) over (partition by (employee_id) order by (date_start)) AS next,
                               COALESCE(cal.hours_per_week, 0) / COALESCE(cal.full_time_required_hours, 1) as work_time_rate
                          FROM hr_contract ctr
                          JOIN resource_calendar cal on cal.id = ctr.resource_calendar_id
                         WHERE employee_id IS NOT NULL AND date_start IS NOT NULL
                           AND resource_calendar_id IS NOT NULL AND state in ('open', 'close')
                      ORDER BY date_start ASC
                    )
        UPDATE hr_contract
           SET calendar_changed=TRUE
         WHERE id IN (
                SELECT curr.id
                  FROM helper curr
                  JOIN helper prev on prev.id = curr.previous
                 WHERE curr.work_time_rate != prev.work_time_rate
                 UNION
                SELECT curr.id
                  FROM helper curr
                  JOIN helper next on next.id = curr.next
                 WHERE curr.work_time_rate != next.work_time_rate
        )
        """
    )

    util.remove_record(cr, "hr_payroll.menu_hr_payroll_employees_configuration")
    util.remove_record(cr, "hr_payroll.menu_hr_payroll_contracts_to_review")
