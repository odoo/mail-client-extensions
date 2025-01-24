from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT c.id
          FROM res_company c
          JOIN res_partner p
            ON p.id = c.partner_id
         WHERE p.country_id = %s
        """,
        [util.ref(cr, "base.au")],
    )

    cids = tuple(c[0] for c in cr.fetchall())

    # Fields moved from hr.contract to hr.employee
    util.create_column(cr, "hr_employee", "l10n_au_withholding_variation", "varchar")
    util.create_column(cr, "hr_employee", "l10n_au_employment_basis_code", "varchar")
    util.create_column(cr, "hr_employee", "l10n_au_withholding_variation_amount", "float8")
    util.create_column(cr, "hr_employee", "l10n_au_work_country_id", "int4")
    # Fields moved from hr.payroll.structure.type to hr.employee
    util.create_column(cr, "hr_employee", "l10n_au_tax_treatment_category", "varchar")
    util.create_column(cr, "hr_employee", "l10n_au_income_stream_type", "varchar")
    if cids:
        cr.execute(
            """
                UPDATE hr_employee e
                   SET l10n_au_withholding_variation = c.l10n_au_withholding_variation,
                       l10n_au_employment_basis_code = c.l10n_au_employment_basis_code,
                       l10n_au_withholding_variation_amount = c.l10n_au_withholding_variation_amount,
                       l10n_au_work_country_id = c.l10n_au_country_code,
                       l10n_au_tax_treatment_category = COALESCE(s.l10n_au_tax_treatment_category, 'R'),
                       l10n_au_income_stream_type = COALESCE(s.l10n_au_income_stream_type, 'SAW')
                  FROM hr_contract c
                  LEFT JOIN hr_payroll_structure_type s
                    ON c.structure_type_id = s.id
                 WHERE c.employee_id = e.id
                   AND e.company_id IN %s
                """,
            [cids],
        )

    fields_to_delete = [
        ("hr.contract", "l10n_au_tax_treatment_option"),
        ("hr.contract", "l10n_au_tax_treatment_code"),
        ("hr.contract", "l10n_au_employment_basis_code"),
        ("hr.contract", "l10n_au_income_stream_type"),
        ("hr.contract", "l10n_au_country_code"),
        ("hr.contract", "l10n_au_withholding_variation"),
        ("hr.contract", "l10n_au_withholding_variation_amount"),
        ("hr.contract", "l10n_au_workplace_giving_type"),
        ("hr.employee", "l10n_au_scale"),
        ("hr.payslip", "l10n_au_allowance_withholding"),
        ("hr.payroll.structure.type", "l10n_au_tax_treatment_category"),
        ("hr.payroll.structure.type", "l10n_au_income_stream_type"),
        ("hr.payroll.report", "x_l10n_au_gross_commission"),
    ]

    for model, field in fields_to_delete:
        util.remove_field(cr, model, field)

    if cids:
        cr.execute(
            "UPDATE hr_contract SET structure_type_id = %s WHERE company_id IN %s",
            [util.ref(cr, "l10n_au_hr_payroll.structure_type_schedule_1"), cids],
        )
        cr.execute(
            "UPDATE hr_payslip SET struct_id = %s WHERE company_id IN %s",
            [util.ref(cr, "l10n_au_hr_payroll.hr_payroll_structure_au_regular"), cids],
        )

    # Finally delete all old salary struct, struct_type and rules
    records_to_delete = [
        # Rules
        "l10n_au_hr_payroll.l10n_au_ote_structure_3",
        "l10n_au_hr_payroll.l10n_au_termination_etp_gross_structure_3",
        "l10n_au_hr_payroll.l10n_au_termination_etp_tax_free_structure_3",
        "l10n_au_hr_payroll.l10n_au_termination_etp_structure_3",
        "l10n_au_hr_payroll.l10n_au_termination_leave_structure_3",
        "l10n_au_hr_payroll.l10n_au_withholding_actors_structure_3",
        "l10n_au_hr_payroll.l10n_au_allowance_withholding_structure_3",
        "l10n_au_hr_payroll.l10n_au_termination_etp_withholding_structure_3",
        "l10n_au_hr_payroll.l10n_au_termination_leave_withholding_structure_3",
        "l10n_au_hr_payroll.l10n_au_withholding_net_structure_3",
        "l10n_au_hr_payroll.l10n_au_child_support_structure_3",
        "l10n_au_hr_payroll.l10n_au_allowance_structure_3",
        "l10n_au_hr_payroll.l10n_au_super_contribution_structure_3",
        "l10n_au_hr_payroll.l10n_au_ote_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_workplace_giving_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_termination_etp_gross_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_termination_etp_tax_free_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_termination_etp_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_termination_leave_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_withholding_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_termination_etp_withholding_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_termination_leave_withholding_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_withholding_net_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_child_support_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_allowance_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_super_contribution_structure_3_promo",
        "l10n_au_hr_payroll.l10n_au_ote_structure_2",
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_total_structure_2",
        "l10n_au_hr_payroll.l10n_au_workplace_giving_structure_2",
        "l10n_au_hr_payroll.l10n_au_termination_etp_gross_structure_2",
        "l10n_au_hr_payroll.l10n_au_termination_etp_tax_free_structure_2",
        "l10n_au_hr_payroll.l10n_au_termination_etp_structure_2",
        "l10n_au_hr_payroll.l10n_au_termination_leave_structure_2",
        "l10n_au_hr_payroll.l10n_au_withholding_structure_2",
        "l10n_au_hr_payroll.l10n_au_allowance_withholding_structure_2",
        "l10n_au_hr_payroll.l10n_au_termination_etp_withholding_structure_2",
        "l10n_au_hr_payroll.l10n_au_termination_leave_withholding_structure_2",
        "l10n_au_hr_payroll.l10n_au_withholding_net_structure_2",
        "l10n_au_hr_payroll.l10n_au_child_support_structure_2",
        "l10n_au_hr_payroll.l10n_au_allowance_structure_2",
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_other_structure_2",
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_structure_2",
        "l10n_au_hr_payroll.l10n_au_super_contribution_structure_2",
        "l10n_au_hr_payroll.l10n_au_ote_structure_5",
        "l10n_au_hr_payroll.l10n_au_workplace_giving_structure_5",
        "l10n_au_hr_payroll.l10n_au_withholding_lumpsum_structure_5",
        "l10n_au_hr_payroll.l10n_au_super_contribution_lumpsum_structure_5",
        "l10n_au_hr_payroll.l10n_au_ote_structure_no_tfn",
        "l10n_au_hr_payroll.l10n_au_extra_pay_structure_no_tfn",
        "l10n_au_hr_payroll.l10n_au_workplace_giving_structure_no_tfn",
        "l10n_au_hr_payroll.l10n_au_withholding_no_tfn",
        "l10n_au_hr_payroll.l10n_au_withholding_net_no_tfn",
        "l10n_au_hr_payroll.l10n_au_allowance_structure_no_tfn",
        "l10n_au_hr_payroll.l10n_au_ote_structure_4",
        "l10n_au_hr_payroll.l10n_au_return_to_work_structure_4",
        "l10n_au_hr_payroll.l10n_au_workplace_giving_structure_4",
        "l10n_au_hr_payroll.l10n_au_return_to_work_gross_structure_4",
        "l10n_au_hr_payroll.l10n_au_withholding_return_to_work_structure_4",
        "l10n_au_hr_payroll.l10n_au_withholding_total_return_to_work_structure_4",
        "l10n_au_hr_payroll.l10n_au_child_support_return_to_work_structure_4",
        "l10n_au_hr_payroll.l10n_au_return_to_work_structure_4_net_salary",
        "l10n_au_hr_payroll.l10n_au_super_contribution_structure_4",
        "l10n_au_hr_payroll.l10n_au_ote_structure_15",
        "l10n_au_hr_payroll.l10n_au_extra_pay_structure_15",
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_total_structure_15",
        "l10n_au_hr_payroll.l10n_au_workplace_giving_structure_15",
        "l10n_au_hr_payroll.l10n_au_withholding_whm_structure_15",
        "l10n_au_hr_payroll.l10n_au_withholding_net_structure_15",
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_other_structure_15",
        "l10n_au_hr_payroll.l10n_au_salary_sacrifice_structure_15",
        "l10n_au_hr_payroll.l10n_au_super_contribution_structure_15",
        # Expense rules for accounting module
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_2",
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_3",
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_3_promo",
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_9",
        "l10n_au_hr_payroll_account.l10n_au_salary_expense_refund_structure_15",
        # Structures
        "l10n_au_hr_payroll.hr_payroll_structure_au_horticulture",
        "l10n_au_hr_payroll.hr_payroll_structure_au_actor",
        "l10n_au_hr_payroll.hr_payroll_structure_au_actor_promotional",
        "l10n_au_hr_payroll.hr_payroll_structure_au_return_to_work",
        "l10n_au_hr_payroll.hr_payroll_structure_au_lumpsum",
        "l10n_au_hr_payroll.hr_payroll_structure_au_senior",
        "l10n_au_hr_payroll.hr_payroll_structure_au_whm",
        "l10n_au_hr_payroll.hr_payroll_structure_au_no_tfn",
        # Struct type
        "l10n_au_hr_payroll.structure_type_schedule_2",
        "l10n_au_hr_payroll.structure_type_schedule_3",
        "l10n_au_hr_payroll.structure_type_schedule_4",
        "l10n_au_hr_payroll.structure_type_schedule_5",
        "l10n_au_hr_payroll.structure_type_schedule_9",
        "l10n_au_hr_payroll.structure_type_schedule_15",
        "l10n_au_hr_payroll.structure_type_no_tfn",
        # Rule Parameters
        "l10n_au_hr_payroll.rule_parameter_medicare_levy",
        "l10n_au_hr_payroll.rule_parameter_underage_schedule_3",
        "l10n_au_hr_payroll.rule_parameter_withholding_coefficients",
        # Payslip input types
        "l10n_au_hr_payroll.input_gross_bonuses_and_commissions",
        "l10n_au_hr_payroll.input_gross_cdep",
        "l10n_au_hr_payroll.input_extra_pay",
        "l10n_au_hr_payroll.input_cents_per_kilometer_4",
        "l10n_au_hr_payroll.input_overseas_accommodation_allowance_2",
    ]
    util.delete_unused(cr, *records_to_delete)

    util.rename_field(cr, "hr.employee", "l10n_au_previous_id_bms", "l10n_au_previous_payroll_id")

    cr.execute(
        "UPDATE hr_employee SET l10n_au_child_support_garnishee_amount=0 WHERE l10n_au_child_support_garnishee_amount>1"
    )

    util.create_column(cr, "hr_payslip", "l10n_au_extra_negotiated_super", "float8")
    util.create_column(cr, "hr_payslip", "l10n_au_extra_compulsory_super", "float8")
    util.create_column(cr, "hr_payslip", "l10n_au_salary_sacrifice_superannuation", "float8")
    util.create_column(cr, "hr_payslip", "l10n_au_salary_sacrifice_other", "float8")

    query = """
        UPDATE hr_payslip p
           SET l10n_au_extra_negotiated_super = 0,
               l10n_au_extra_compulsory_super = 0,
               l10n_au_salary_sacrifice_superannuation = c.l10n_au_salary_sacrifice_superannuation,
               l10n_au_salary_sacrifice_other = c.l10n_au_salary_sacrifice_other
          FROM hr_contract c
         WHERE c.id = p.contract_id
           AND p.company_id IN %s
        """
    if cids:
        util.explode_execute(cr, cr.mogrify(query, [cids]).decode(), table="hr_payslip", alias="p")

    util.remove_field(cr, "res.company", "l10n_au_sfei")
    util.remove_field(cr, "res.config.settings", "l10n_au_sfei")
    util.remove_field(cr, "hr.employee", "l10n_au_child_support_garnishee")

    util.remove_view(cr, "l10n_au_hr_payroll.l10n_au_payevnt_0004_form_wizard")
    util.remove_view(cr, "l10n_au_hr_payroll.l10n_au_payevent0004_action_view_tree")

    if util.module_installed(cr, "l10n_au_hr_payroll_account"):
        eb = util.expand_braces
        util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{,_account}.l10n_au_payevent_transaction_sequence"))
        util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{,_account}.l10n_au_payevent_transaction_sequence_demo"))
        util.rename_xmlid(cr, *eb("l10n_au_hr_payroll{,_account}.payevent_0004_xml_report"))
        util.rename_xmlid(
            cr,
            "l10n_au_hr_payroll.l10n_au_payevent0004_action",
            "l10n_au_hr_payroll_account.l10n_au_stp_action",
        )
        util.move_model(cr, "l10n_au.payevnt.0004", "l10n_au_hr_payroll", "l10n_au_hr_payroll_account")
        util.rename_xmlid(
            cr,
            "l10n_au_hr_payroll.menu_l10n_au_l10n_au_payevent0004",
            "l10n_au_hr_payroll_account.menu_l10n_au_l10n_au_stp",
        )
        util.move_model(cr, "l10n_au.payevnt.emp.0004", "l10n_au_hr_payroll", "l10n_au_hr_payroll_account")
        util.rename_model(cr, "l10n_au.payevnt.0004", "l10n_au.stp")
        util.rename_model(cr, "l10n_au.payevnt.emp.0004", "l10n_au.stp.emp")
        util.rename_field(cr, "l10n_au.stp.emp", "payevnt_0004_id", "stp_id")
        util.remove_field(cr, "l10n_au.stp.emp", "payslip_currency_id")
        util.remove_field(cr, "l10n_au.stp.emp", "payslip_id")
        util.remove_field(cr, "l10n_au.stp", "intermediary")
        util.remove_field(cr, "l10n_au.stp", "previous_id_bms")
    else:
        util.delete_model(cr, "l10n_au.payevnt.0004")
        util.delete_model(cr, "l10n_au.payevnt.emp.0004")
        util.delete_unused(
            cr,
            "l10n_au_hr_payroll.l10n_au_payevent_transaction_sequence_demo",
            "l10n_au_hr_payroll.l10n_au_payevent_transaction_sequence",
            "l10n_au_hr_payroll.l10n_au_payevent0004_action",
        )
        util.remove_view(cr, "l10n_au_hr_payroll.payevent_0004_xml_report")
        util.remove_menus(cr, [util.ref(cr, "l10n_au_hr_payroll.menu_l10n_au_l10n_au_payevent0004")])
