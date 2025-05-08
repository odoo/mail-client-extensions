from odoo.upgrade import util
from odoo.upgrade.util.hr_payroll import remove_salary_rule


def migrate(cr, version):
    util.remove_view(cr, "hr_payroll.view_resource_calendar_search_inherit_payroll")
    util.remove_view(cr, "hr_payroll.resource_calendar_view_tree")
    util.remove_view(cr, "hr_payroll.payroll_resource_calendar_view_form")
    util.force_noupdate(cr, "hr_payroll.hr_work_entry_type_out_of_contract")

    """
    This script will archive all salary rules that have no reference
    in xml files with the codes BASIC, GROSS, ATTACH_SALARY,
    ASSIG_SALARY, CHILD_SUPPORT, DEDUCTION, REIMBURSEMENT and NET
    since they are going to be replaced by fully translatable salary rulepayroll_structure.
    The ch monthly structure is the only one that will keep these for now.
    """
    remove_salary_rule(cr, "l10n_be_hr_payroll.cp200_employees_thirteen_month_mis_ex_onss")

    cr.execute(r"""
       WITH filtered_salary_rule AS (
           SELECT rule.id
             FROM hr_salary_rule rule
             JOIN hr_payroll_structure structure
               ON structure.id = rule.struct_id
        LEFT JOIN ir_model_data
               ON ir_model_data.res_id = rule.id
              AND ir_model_data.model = 'hr.salary.rule'
              AND (ir_model_data.module LIKE 'l10n\_%\_hr\_payroll'
                   OR ir_model_data.module = 'hr_payroll')
            WHERE ir_model_data IS NULL
              AND structure.code IS DISTINCT FROM 'CHMONTHLY'
              AND rule.code IN (
                  'BASIC', 'GROSS', 'ATTACH_SALARY', 'ASSIG_SALARY',
                  'CHILD_SUPPORT', 'DEDUCTION', 'REIMBURSEMENT', 'NET'
              )
       )

       UPDATE hr_salary_rule
          SET active = false
         FROM filtered_salary_rule
        WHERE hr_salary_rule.id = filtered_salary_rule.id
    """)

    util.remove_records(
        cr,
        "ir.actions.server",
        [
            util.ref(cr, f"hr_payroll.action_hr_payroll_{suffix}")
            for suffix in ["draft", "compute_payroll", "confirm_payroll", "cancel_payroll", "recompute_whole_sheet"]
        ],
    )
