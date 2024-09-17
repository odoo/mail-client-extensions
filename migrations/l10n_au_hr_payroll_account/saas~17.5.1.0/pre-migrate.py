from odoo.upgrade import util


def migrate(cr, version):
    records_to_delete = [
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_2",
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_3",
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_3_promo",
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_9",
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_15",
    ]
    util.delete_unused(cr, *records_to_delete)

    util.create_column(cr, "l10n_au_super_account", "company_id", "int4")
    cr.execute(
        """
        UPDATE l10n_au_super_account
           SET company_id = e.company_id
          FROM hr_employee e
         WHERE e.id = l10n_au_super_account.employee_id
        """
    )

    util.remove_field(cr, "l10n_au.super.stream.line", "at_work_indicator")
