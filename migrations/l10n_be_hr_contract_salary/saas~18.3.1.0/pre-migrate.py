from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr,
        "l10n_be_hr_contract_salary.hr_contract_salary_payroll_resume_gross_cp200",
        util.update_record_from_xml,
        fields=["code"],
    )
    util.if_unchanged(
        cr,
        "l10n_be_hr_contract_salary.hr_contract_salary_resume_monthly_cash",
        util.update_record_from_xml,
        fields=["benefit_ids"],
    )
    util.remove_view(cr, "l10n_be_hr_contract_salary.report_belgium_payslip")
