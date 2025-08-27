from odoo.upgrade import util

account = util.import_script("account/saas~18.5.1.4/pre-remove-tax-tag-invert.py")


def migrate(cr, version):
    util.remove_view(cr, "hr_payroll_account.hr_payslip_run_view_form")

    util.create_column(cr, "hr_version", "analytic_distribution", "jsonb")
    util.create_column(cr, "hr_salary_rule", "analytic_distribution", "jsonb")

    util.explode_execute(
        cr,
        """
        UPDATE hr_version hv
           SET analytic_distribution = jsonb_build_object(hv.analytic_account_id::text, 100.0)
         WHERE hv.analytic_account_id IS NOT NULL
        """,
        table="hr_version",
        alias="hv",
    )

    util.explode_execute(
        cr,
        """
        UPDATE hr_salary_rule hsr
           SET analytic_distribution = jsonb_build_object(hsr.analytic_account_id::text, 100.0)
         WHERE hsr.analytic_account_id IS NOT NULL
        """,
        table="hr_salary_rule",
        alias="hsr",
    )

    util.remove_field(cr, "hr.version", "analytic_account_id")
    util.remove_field(cr, "hr.salary.rule", "analytic_account_id")

    util.remove_menus(cr, [util.ref(cr, "hr_payroll_account.menu_hr_employee_bank_account")])

    account.update_m2m_tag_rel(cr, "hr_salary_rule_debit_tag_rel")
    account.update_m2m_tag_rel(cr, "hr_salary_rule_credit_tag_rel")
