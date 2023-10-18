from odoo.addons.base.maintenance.migrations import util


def remove_salary_rule(cr, xmlid):
    rid = util.ref(cr, xmlid)
    cr.execute(
        r"""
        SELECT f.name
          FROM ir_model_fields f,
               hr_salary_rule r
          JOIN hr_payroll_structure s
            ON r.struct_id = s.id
     LEFT JOIN res_country c
            ON s.country_id = c.id
         WHERE r.id = %s
           AND f.model = 'hr.payroll.report'
           AND f.name = regexp_replace(
                            concat_ws(
                                '_',
                                'x_l10n',
                                COALESCE(lower(c.code), 'xx'),
                                lower(r.code)
                            ),
                            '[\.\- ]',
                            '_'
                        )
        """,
        [rid],
    )
    for (fname,) in cr.fetchall():
        util._logger.info(
            "Removing field %r from model 'hr.payroll.report' since salary rule %r is being removed",
            fname,
            xmlid,
        )
        util.remove_field(cr, "hr.payroll.report", fname)
    util.delete_unused(cr, xmlid)


def migrate(cr, version):
    if not util.version_between("16.0", "17.0"):
        return
    eb = util.expand_braces

    # l10n_ke_hr_payroll/data/hr_salary_rule_data.xml
    util.rename_xmlid(cr, *eb("l10n_ke_hr_payroll.l10n_ke_employees{_salary,}_insurance_relief"))
    remove_salary_rule(cr, "l10n_ke_hr_payroll.l10n_ke_employees_salary_mortgage_interest")
    remove_salary_rule(cr, "l10n_ke_hr_payroll.l10n_ke_employees_salary_nssf")

    # l10n_ke_hr_payroll/data/hr_salary_rule_category_data.xml
    util.rename_xmlid(cr, *eb("l10n_ke_hr_payroll.{hr_salary_rule_category_relief,RELIEF}"))
    util.rename_xmlid(cr, *eb("l10n_ke_hr_payroll.{hr_salary_rule_category_tax_exemption,EXEMPTION}"))
    util.remove_record(cr, "l10n_ke_hr_payroll.hr_salary_rule_category_paye")

    # l10n_ke_hr_payroll/views/hr_employee_views.xml
    util.remove_view(cr, "l10n_ke_hr_payroll.hr_employee_view_form")
