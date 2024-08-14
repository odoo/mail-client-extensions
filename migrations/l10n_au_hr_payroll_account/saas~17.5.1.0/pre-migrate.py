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
