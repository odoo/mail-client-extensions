# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    Payslip = env["hr.payslip"]

    all_we_types = env["hr.work.entry.type"].search([])

    cr.execute("SELECT payslip_id FROM hr_payslip_worked_days WHERE amount IS NULL GROUP BY payslip_id")
    for (payslip_id,) in util.log_progress(cr.fetchall(), "payslip"):
        payslip = Payslip.browse(payslip_id)

        contract = payslip_id.contract_id
        if not contract.resource_calendar_id:
            continue

        paid_work_entry_types = all_we_types - payslip.struct_id.unpaid_work_entry_type_ids
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
