# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    Payslip = env["hr.payslip"]

    cr.execute(
        """
        WITH leaves AS
        (
            SELECT l.id,
                em.name,
                l.date_from,
                CASE l.number_of_days
                    WHEN 0 THEN
                        l.date_to + 1 * INTERVAL '1 microsecond'
                    ELSE
                        l.date_from +
                        l.number_of_days *
                        CASE t.request_unit
                            WHEN 'day' THEN r.hours_per_day
                            WHEN 'half-day' THEN r.hours_per_day/2.0
                            WHEN 'hour' THEN 1
                            ELSE 0
                        END * INTERVAL '1 hour'
                END AS date_to_update
            FROM hr_leave l
            JOIN hr_leave_type t ON l.holiday_status_id = t.id
            JOIN hr_employee em ON l.employee_id = em.id
            JOIN resource_calendar r ON r.id = em.resource_calendar_id
           WHERE l.date_from = l.date_to
             AND l.number_of_days IS NOT NULL
        ),
        update_hr_leave AS
        (
            UPDATE hr_leave hl SET date_to = leaves.date_to_update
              FROM leaves
             WHERE leaves.id = hl.id
        )
        UPDATE resource_calendar_leaves hl SET date_to = leaves.date_to_update
          FROM leaves
         WHERE leaves.id = hl.holiday_id
        RETURNING leaves.id, leaves.name, leaves.date_from, leaves.date_to_update"""
    )
    if cr.rowcount:
        msg = """The following hr_leaves have a date_from equal to date_to causes issues during the upgrade.
            The date_from has been adapted to the number of leave days taken, or if the number of days was set
            to zero, the interval has been set to span 1 microsecond.
            Please check carefully those leaves after the upgrade.
            %s
        """ % ",".join(
            [
                "hr_leave: %s, user: %s, date_from :%s, date_to (original): %s, date_date (updated): %s"
                % (
                    r["id"],
                    r["name"],
                    r["date_from"],
                    r["date_from"],
                    r["date_to_update"],
                )
                for r in cr.dictfetchall()
            ]
        )
        util.add_to_migration_reports(msg)

    all_we_types = env["hr.work.entry.type"].search([])
    cr.execute("SELECT payslip_id FROM hr_payslip_worked_days WHERE amount IS NULL GROUP BY payslip_id")
    for (payslip_id,) in util.log_progress(cr.fetchall(), util._logger, "payslip"):
        payslip = Payslip.browse(payslip_id)

        contract = payslip.contract_id
        if not contract.resource_calendar_id:
            continue

        paid_work_entry_types = all_we_types - payslip.struct_id.unpaid_work_entry_type_ids
        if util.version_gte("saas~12.5"):
            contract.date_generated_from = contract.date_generated_to = payslip.date_to
            work_hours = contract._get_work_hours(payslip.date_from, payslip.date_to)
            total_hours = sum(work_hours.values()) or 1
            paid_amount = payslip._get_contract_wage()
            work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
            for work_entry_type_id, hours in work_hours_ordered:
                if work_entry_type_id in paid_work_entry_types.ids:
                    cr.execute(
                        """
                        UPDATE hr_payslip_worked_days
                           SET amount = %s * %s / %s
                         WHERE amount IS NULL
                           AND payslip_id = %s
                           AND work_entry_type_id = %s
                    """,
                        [hours, paid_amount, total_hours, payslip_id, work_entry_type_id],
                    )

        else:
            total_paid_days = contract._get_work_data(paid_work_entry_types, payslip.date_from, payslip.date_to)["days"]

            if total_paid_days:
                paid_amount = payslip._get_paid_amount()

                cr.execute(
                    """
                    UPDATE hr_payslip_worked_days
                       SET amount = number_of_days / %s * %s
                     WHERE amount IS NULL
                       AND payslip_id = %s
                """,
                    [total_paid_days, paid_amount, payslip_id],
                )

    cr.execute("UPDATE hr_payslip_worked_days SET amount = 0 WHERE amount IS NULL")

    # TODO? create a "normal work entry type" line with remaining days?
