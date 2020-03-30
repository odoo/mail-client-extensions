# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    Payslip = env["hr.payslip"]

    all_we_types = env["hr.work.entry.type"].search([])

    cr.execute("SELECT payslip_id FROM hr_payslip_worked_days WHERE amount IS NULL GROUP BY payslip_id")
    for (payslip_id,) in util.log_progress(cr.fetchall(), "payslip"):
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
