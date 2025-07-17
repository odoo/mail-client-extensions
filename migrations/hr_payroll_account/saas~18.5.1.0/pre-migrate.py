from odoo.upgrade import util


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
