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

    util.remove_field(cr, "hr.employee", "l10n_au_super_account_id")

    util.rename_xmlid(
        cr,
        "l10n_au_hr_payroll.l10n_au_workplace_giving_structure_16",
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_other_structure_15",
    )
    util.rename_xmlid(
        cr,
        "l10n_au_hr_payroll.l10n_au_workplace_giving_structure_17",
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_structure_15",
    )
    util.rename_xmlid(
        cr,
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_total_structure_16",
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_total_structure_15",
    )

    cr.execute("UPDATE hr_contract SET l10n_au_casual_loading = l10n_au_casual_loading / 100;")

    if util.module_installed(cr, "l10n_au_hr_payroll_account"):
        util.rename_xmlid(
            cr,
            *util.expand_braces("l10n_au_hr_payroll{,_account}.hr_payslip_run_form_inherit_l10n_au_hr_payroll"),
        )
    else:
        util.remove_view(cr, "l10n_au_hr_payroll.hr_payslip_run_form_inherit_l10n_au_hr_payroll")

    util.remove_field(cr, "hr.payslip.run", "l10n_au_export_aba_file")
    util.remove_field(cr, "hr.payslip.run", "l10n_au_export_aba_filename")

    util.create_column(cr, "hr_payslip_input_type", "l10n_au_payment_type", "varchar")
    util.create_column(cr, "hr_payslip_input_type", "l10n_au_superannuation_treatment", "varchar")

    ote_col = util.column_exists(cr, "hr_payslip_input_type", "l10n_au_is_ote")
    query = util.format_query(
        cr,
        """
            UPDATE hr_payslip_input_type
               SET l10n_au_payment_type = CASE
                                              WHEN hr_payslip_input_type.l10n_au_is_etp THEN 'etp'
                                              WHEN hr_payslip_input_type.l10n_au_is_allowance THEN 'allowance'
                                          END
                   {}
             WHERE country_id = %s
               AND (  hr_payslip_input_type.l10n_au_is_etp
                   OR hr_payslip_input_type.l10n_au_is_allowance
                   {})
        """,
        util.SQLStr(
            ", l10n_au_superannuation_treatment = CASE WHEN hr_payslip_input_type.l10n_au_is_ote THEN 'ote' END"
            if ote_col
            else ""
        ),
        util.SQLStr("OR hr_payslip_input_type.l10n_au_is_ote" if ote_col else ""),
    )
    cr.execute(query, [util.ref(cr, "base.au")])

    util.remove_field(cr, "hr.payslip.input.type", "l10n_au_is_allowance")
    util.remove_field(cr, "hr.payslip.input.type", "l10n_au_is_etp")
    util.remove_field(cr, "hr.payslip.input.type", "l10n_au_is_ote")
    util.remove_field(cr, "hr.payslip.input.type", "l10n_au_allowance_type")

    util.delete_unused(
        cr,
        "l10n_au_hr_payroll.input_cents_per_kilometre",
        "l10n_au_hr_payroll.input_award_transport_payments",
        "l10n_au_hr_payroll.input_laundry",
        "l10n_au_hr_payroll.input_overtime_meal_allowances",
        "l10n_au_hr_payroll.input_domestic_or_overseas_travel_allowances_and_overseas_accommodation_allowances",
        "l10n_au_hr_payroll.input_tool_allowances",
        "l10n_au_hr_payroll.input_qualification_and_certification_allowances",
        "l10n_au_hr_payroll.input_task_allowances",
        "l10n_au_hr_payroll.input_other_allowances_h1",
        "l10n_au_hr_payroll.input_other_allowances_nd",
        "l10n_au_hr_payroll.input_other_allowances_t1",
        "l10n_au_hr_payroll.input_other_allowances_u1",
        "l10n_au_hr_payroll.input_other_allowances_v1",
        "l10n_au_hr_payroll.input_other_allowances_g1",
    )
