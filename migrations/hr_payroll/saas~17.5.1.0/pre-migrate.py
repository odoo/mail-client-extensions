from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "hr.salary.attachment.report")
    util.remove_menus(cr, [util.ref(cr, "hr_payroll.menu_hr_payroll_attachment_salary_report")])

    util.create_column(cr, "hr_salary_attachment", "other_input_type_id", "int4")

    util.create_column(cr, "hr_payslip_input_type", "active", "boolean", default=True)
    util.create_column(cr, "hr_payslip_input_type", "available_in_attachments", "boolean")
    util.create_column(cr, "hr_payslip_input_type", "is_quantity", "boolean")
    util.create_column(cr, "hr_payslip_input_type", "default_no_end_date", "boolean")

    # Update available_in_attachments, is_quantity and default_no_end_date on
    # hr_payslip_input_type using the values from the first matching
    # hr.salary.attachment.type, based on country_id and code
    cr.execute("""
        WITH cte AS (
            SELECT DISTINCT ON (it.id)
                   it.id,
                   at.is_quantity,
                   at.no_end_date
              FROM hr_payslip_input_type it
              JOIN hr_salary_attachment_type at
                ON it.code = at.code
               AND (  at.country_id = it.country_id
                   OR at.country_id IS NULL)
          ORDER BY it.id,
                   at.country_id = it.country_id DESC NULLS LAST,
                   at.id
        )
        UPDATE hr_payslip_input_type it
           SET available_in_attachments = true,
               is_quantity = cte.is_quantity,
               default_no_end_date = cte.no_end_date
          FROM cte
         WHERE cte.id = it.id
    """)

    # Set other_input_type_id on hr_salary_attachment with the first matching hr_payslip_input_type
    # compared to deduction_type_id, based on country_id and code
    util.explode_execute(
        cr,
        """
            WITH cte AS (
                SELECT DISTINCT ON (a.id)
                       a.id AS attachment_id,
                       it.id AS other_input_type_id
                  FROM hr_salary_attachment a
                  JOIN hr_salary_attachment_type at
                    ON a.deduction_type_id = at.id
                  JOIN hr_payslip_input_type it
                    ON at.code = it.code
                   AND (  at.country_id = it.country_id
                       OR at.country_id IS NULL)
                 WHERE {parallel_filter}
              ORDER BY a.id,
                       at.country_id = it.country_id DESC NULLS LAST,
                       it.id
            )
            UPDATE hr_salary_attachment a
               SET other_input_type_id = cte.other_input_type_id
              FROM cte
             WHERE cte.attachment_id = a.id
        """,
        table="hr_salary_attachment",
        alias="a",
    )

    util.remove_field(cr, "hr.salary.attachment", "deduction_type_id")

    util.remove_model(cr, "hr.salary.attachment.type")
    util.remove_view(cr, "hr_payroll.hr_salary_attachment_type_view_kanban")
    util.remove_view(cr, "hr_payroll.hr_salary_attachment_type_view_tree")
    util.remove_view(cr, "hr_payroll.hr_salary_attachment_type_view_form")

    util.remove_record(cr, "hr_payroll.ir_rule_hr_salary_attachment_type_multi_company")
    util.remove_record(cr, "hr_payroll.access_hr_salary_attachment_type")
    util.remove_menus(cr, [util.ref(cr, "hr_payroll.menu_hr_salary_attachment_type")])

    if util.module_installed(cr, "l10n_be_hr_payroll"):
        util.move_field_to_module(cr, "hr.employee", "disabled", "l10n_be_hr_payroll", "hr_payroll")

    util.remove_field(cr, "res.config.settings", "module_hr_payroll_account_sepa")
