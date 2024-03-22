from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.payslip.input.type", "l10n_au_etp_cap")
    cr.execute("DROP VIEW IF EXISTS hr_contract_employee_report")
    util.alter_column_type(
        cr,
        "hr_contract",
        "l10n_au_withholding_variation",
        "varchar",
        using="CASE WHEN {0} IS TRUE THEN 'salaries' ELSE 'none' END",
    )

    # Finally we delete the now unused rules and other old termination related records.
    records_to_delete = [
        "l10n_au_hr_payroll.l10n_au_termination_net_salary",
        "l10n_au_hr_payroll.l10n_au_termination_child_support",
        "l10n_au_hr_payroll.l10n_au_termination_withholding",
        "l10n_au_hr_payroll.l10n_au_termination_gross_benefits",
        "l10n_au_hr_payroll.l10n_au_termination_base_benefits",
        "l10n_au_hr_payroll.l10n_au_termination_leave",
        "l10n_au_hr_payroll.l10n_au_termination_etp_gross",
        "l10n_au_hr_payroll.l10n_au_termination_etp_tax_free",
        "l10n_au_hr_payroll.l10n_au_termination_etp",
        "l10n_au_hr_payroll.l10n_au_termination_etp_withholding",
        "l10n_au_hr_payroll.l10n_au_termination_leave_withholding",
        "l10n_au_hr_payroll.rule_category_etp_gross",
        "l10n_au_hr_payroll.rule_category_etp_withhold",
        "l10n_au_hr_payroll.rule_category_leave_base",
        "l10n_au_hr_payroll.rule_category_leave_withhold",
        "l10n_au_hr_payroll.rule_parameter_etp_withholding",
        "l10n_au_hr_payroll.hr_payroll_structure_au_termination",
        "l10n_au_hr_payroll.structure_type_schedule_11_and_7",
    ]
    util.delete_unused(cr, *records_to_delete)
