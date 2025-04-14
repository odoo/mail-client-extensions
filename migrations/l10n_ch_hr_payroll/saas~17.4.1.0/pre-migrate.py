from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.salary.rule", "l10n_ch_comp_ac_included")
    util.remove_field(cr, "hr.salary.rule", "l10n_ch_october_statement")

    util.remove_view(cr, "l10n_ch_hr_payroll.hr_salary_attachment_view_search")
    util.remove_view(cr, "l10n_ch_hr_payroll.hr_salary_attachment_view_form")
    util.remove_view(cr, "l10n_ch_hr_payroll.hr_salary_attachment_view_tree")
    util.remove_view(cr, "l10n_ch_hr_payroll.hr_salary_attachment_type_view_form")

    insurance_tables = [
        "l10n_ch_additional_accident_insurance",
        "l10n_ch_compensation_fund",
        "l10n_ch_sickness_insurance",
        "l10n_ch_social_insurance",
        "l10n_ch_accident_insurance",
    ]
    for insurance_table in insurance_tables:
        if not util.column_exists(cr, insurance_table, "insurance_code"):
            util.create_column(cr, insurance_table, "insurance_code", "varchar")
            cr.execute(
                util.format_query(
                    cr,
                    "UPDATE {insurance_table} SET insurance_code=insurance_company",
                    insurance_table=insurance_table,
                )
            )
        insurance_model = util.model_of_table(cr, insurance_table)
        cr.execute(
            """
            SELECT 1
              FROM ir_model_fields
             WHERE name = 'insurance_company'
               AND model = %(insurance_model)s
               AND ttype = 'selection'
            """,
            {"insurance_model": insurance_model},
        )
        if cr.rowcount:
            cr.execute(
                util.format_query(
                    cr,
                    """
                        UPDATE {insurance_table} i
                           SET insurance_company = s.name->>'en_US'
                          FROM ir_model_fields_selection s
                          JOIN ir_model_fields f ON s.field_id = f.id
                         WHERE i.insurance_company = s.value
                           AND f.name = 'insurance_company'
                           AND f.model = %(insurance_model)s
                    """,
                    insurance_table=insurance_table,
                ),
                {"insurance_model": insurance_model},
            )
        cr.execute(
            """
                DELETE FROM ir_model_fields_selection s
                      USING ir_model_fields f
                      WHERE s.field_id = f.id
                        AND f.name = 'insurance_company'
                        AND f.model = %(insurance_model)s
            """,
            {"insurance_model": insurance_model},
        )

    hr_salary_rule = [
        "l10n_ch_employees_indemnity_maternity_2",
        "l10n_ch_employees_indemnity_illness_2",
        "l10n_ch_employees_indemnity_accident_2",
        "l10n_ch_employees_company_car_employee_2",
        "l10n_ch_employees_ijm_comp",
        "l10n_ch_employees_ijm",
        "l10n_ch_employees_ijm_salary",
        "l10n_ch_employees_laac_comp",
        "l10n_ch_employees_laac_salary",
        "l10n_ch_employees_aanp_salary",
    ]
    util.delete_unused(cr, *[f"l10n_ch_hr_payroll.{xmlid}" for xmlid in hr_salary_rule])
