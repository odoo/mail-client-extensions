# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.payslip", "details_by_salary_rule_category")

    util.create_column(cr, "hr_payslip_line", "name", "varchar")
    util.create_column(cr, "hr_payslip_line", "note", "text")
    util.create_column(cr, "hr_payslip_line", "sequence", "int4")
    util.create_column(cr, "hr_payslip_line", "code", "varchar")
    util.create_column(cr, "hr_payslip_line", "category_id", "int4")
    util.create_column(cr, "hr_payslip_line", "register_id", "int4")

    cr.execute(
        """
        UPDATE hr_payslip_line l
           SET name = r.name,
               note = r.note,
               sequence = r.sequence,
               code = r.code,
               category_id=r.category_id,
               register_id=r.register_id
          FROM hr_salary_rule r
         WHERE r.id = l.salary_rule_id
    """
    )
    # `hr.payslip.line` lost it's inheritance from `hr.salary.rule`
    # remove old inherits auto-related fields
    for field in {
        "active",
        "parent_rule_id",
        "condition_select",
        "condition_range",
        "condition_python",
        "condition_range_min",
        "condition_range_max",
        "amount_python_compute",
        "amount_percentage_base",
        "child_ids",
        "input_ids",
        # and fields from `hr_payroll_account`
        "analytic_account_id",
        "account_tax_id",
        "account_debit",
        "account_credit",
    }:
        util.remove_field(cr, "hr.payslip.line", field)

    if util.version_gte("saas~12.3"):
        util.remove_column(cr, "hr_payslip_line", "company_id")  # now a related
    else:
        util.remove_field(cr, "hr.payslip.line", "company_id")  # gone in saas~12.{1,2}

    util.remove_field(cr, "hr.salary.rule", "input_ids")

    # now related fields
    util.remove_column(cr, "hr_payslip_worked_days", "contract_id")
    util.remove_column(cr, "hr_payslip_input", "contract_id")

    util.remove_field(cr, "res.config.settings", "module_account_accountant")

    util.remove_model(cr, "hr.rule.input")
    util.remove_model(cr, "report.hr_payroll.report_payslipdetails")
    util.remove_record(cr, "hr_payroll.payslip_details_report")
    util.remove_view(cr, "hr_payroll.report_payslipdetails")

    util.remove_view(cr, "hr_payroll.hr_contract_advantage_template_view_form")
    util.remove_view(cr, "hr_payroll.hr_contract_advantage_template_view_tree")
    util.remove_record(cr, "hr_payroll.hr_contract_advantage_template_menu_action")
    util.remove_record(cr, "hr_payroll.hr_contract_advantage_template_action")

    util.delete_unused(cr, "hr_payroll.hr_salary_rule_sales_commission")
    util.delete_unused(cr, "hr_payroll.hr_payroll_rules_child_alw")
    util.delete_unused(cr, "hr_payroll.hr_payroll_rules_baremeIII")
    util.delete_unused(cr, "hr_payroll.hr_payroll_rules_baremeII")
    util.delete_unused(cr, "hr_payroll.hr_payroll_rules_mis_ex_onss_2")
    util.delete_unused(cr, "hr_payroll.hr_payroll_rules_mis_ex_onss_1")
