# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    without_pf_rules = [
        "rule_parameter_basic_without_pf_value",
        "rule_parameter_basic_without_pf",
    ]
    for rule in without_pf_rules:
        util.delete_unused(cr, f"l10n_in_hr_payroll.{rule}")

    struct_id = util.ref(cr, "l10n_in_hr_payroll.structure_without_pf")
    cr.execute(
        """
        DELETE
          FROM hr_salary_rule r
         WHERE r.struct_id=%s
           AND NOT EXISTS (SELECT 1
                             FROM hr_payslip_line l
                            WHERE l.salary_rule_id = r.id)
        """,
        [struct_id],
    )
    util.delete_unused(cr, "l10n_in_hr_payroll.structure_without_pf")
    util.rename_xmlid(
        cr,
        "l10n_in_hr_payroll.structure_with_pf",
        "l10n_in_hr_payroll.hr_payroll_structure_in_employee_salary",
    )
    util.rename_xmlid(
        cr,
        "l10n_in_hr_payroll.rule_parameter_professional_tax_2022",
        "l10n_in_hr_payroll.l10n_in_rule_parameter_professional_tax_value",
    )

    with_pf_rules = [
        "rule_parameter_basic_with_pf",
        "rule_parameter_basic_with_pf_value",
        "rule_parameter_professional_tax",
        "rule_parameter_leave_days",
        "rule_parameter_leave_days_value",
        "rule_parameter_std_awl",
        "rule_parameter_std_awl_value",
        "hr_salary_rule_hra_with_pf",
        "hr_salary_rule_std_with_pf",
        "hr_salary_rule_bonus_with_pf",
        "hr_salary_rule_lta_with_pf",
        "hr_salary_rule_spl_with_pf",
        "hr_salary_rule_p_bonus_with_pf",
        "hr_salary_rule_leave_with_pf",
        "hr_salary_rule_pt_with_pf",
        "hr_salary_rule_pf_with_pf",
        "hr_salary_rule_pfe_with_pf",
        "hr_salary_rule_attach_salary_with_pf",
        "hr_salary_rule_assig_salary_with_pf",
    ]
    for rule in with_pf_rules:
        util.rename_xmlid(
            cr,
            f"l10n_in_hr_payroll.{rule}",
            f"l10n_in_hr_payroll.l10n_in_{rule}".replace("_with_pf", ""),
        )
