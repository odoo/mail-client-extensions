from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_hk_hr_payroll.hr_payslip_run_form_inherit_l10n_hk_hr_payroll")
    util.rename_field(cr, "hr.employee", "l10n_hk_autopay_emal", "l10n_hk_autopay_email")
    util.rename_field(cr, "hr.employee", "l10n_hk_autopay_mobn", "l10n_hk_autopay_mobile")

    util.create_column(cr, "res_company", "l10n_hk_use_mpf_offsetting", "boolean")
    util.create_column(cr, "res_company", "l10n_hk_eoy_pay_month", "varchar", default="12")
    util.create_column(cr, "hr_payslip", "l10n_hk_includes_eoy_pay", "boolean")
    # We can leave the computed field to False, as it would be the default value.
    util.create_column(cr, "hr_payslip", "l10n_hk_use_mpf_offsetting", "boolean")

    util.remove_field(cr, "hr.work.entry.type", "l10n_hk_non_full_pay")
    util.remove_field(cr, "hr.employee", "l10n_hk_years_of_service")

    # When the reason is 5 is used (custom reason), departure_description is used to fill in the custom reason.
    # If left empty, the resulting file wouldn't be compliant.
    # We can assume that if their number doesn't fall in the legal values (1-5) it is for a custom reason,
    # and thus we update the employee record to reflect that, in case it is used to generate the file to send to the government.
    cr.execute(
        """
        WITH updated_reason AS (
            UPDATE hr_departure_reason departure_reason
               SET l10n_hk_ir56f_code = '5'
             WHERE l10n_hk_ir56f_code IS NOT NULL
               AND l10n_hk_ir56f_code NOT IN ('1', '2', '3', '4', '5')
         RETURNING id, name
        )
        UPDATE hr_version v
           SET departure_description = COALESCE(ur.name->>e.lang, ur.name->>'en_US')
          FROM updated_reason ur, hr_employee e
         WHERE ur.id = v.departure_reason_id
           AND v.departure_description IS NULL
           AND v.employee_id = e.id
        """
    )

    struct_id = util.ref(cr, "l10n_hk_hr_payroll.hr_payroll_structure_cap57_employee_salary")
    query = """
        UPDATE hr_payslip payslip
           SET l10n_hk_includes_eoy_pay = TRUE
          FROM res_company company
          JOIN res_partner partner
            ON partner.id = company.partner_id
          JOIN res_country country
            ON country.id = partner.country_id
         WHERE payslip.company_id = company.id
           AND EXTRACT(MONTH FROM payslip.date_to) = company.l10n_hk_eoy_pay_month::INTEGER
           AND EXISTS (
                SELECT 1
                  FROM hr_payslip other_slip
                 WHERE other_slip.employee_id = payslip.employee_id
                   AND other_slip.state IN ('paid', 'validated')
                   AND other_slip.date_from >= DATE_TRUNC('month', payslip.date_from - INTERVAL '12 month')
                   AND other_slip.date_to < DATE_TRUNC('month', payslip.date_to)
                   AND other_slip.struct_id = %(struct_id)s
            )
        """
    if struct_id:
        util.explode_execute(
            cr, cr.mogrify(query, {"struct_id": struct_id}).decode(), table="hr_payslip", alias="payslip"
        )
