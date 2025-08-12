from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_hr_contract")
    util.remove_field(cr, "res.config.settings", "hr_employee_self_edit")
    util.remove_field(cr, "res.users", "department_id")
    util.remove_field(cr, "res.users", "address_id")
    util.remove_field(cr, "res.users", "employee_parent_id")
    util.remove_field(cr, "res.users", "coach_id")
    util.remove_field(cr, "res.users", "private_lang")
    util.remove_field(cr, "res.users", "distance_home_work")
    util.remove_field(cr, "res.users", "distance_home_work_unit")
    util.remove_field(cr, "res.users", "employee_country_id")
    util.remove_field(cr, "res.users", "identification_id")
    util.remove_field(cr, "res.users", "ssnid")
    util.remove_field(cr, "res.users", "passport_id")
    util.remove_field(cr, "res.users", "sex")
    util.remove_field(cr, "res.users", "birthday")
    util.remove_field(cr, "res.users", "birthday_public_display")
    util.remove_field(cr, "res.users", "place_of_birth")
    util.remove_field(cr, "res.users", "country_of_birth")
    util.remove_field(cr, "res.users", "marital")
    util.remove_field(cr, "res.users", "spouse_complete_name")
    util.remove_field(cr, "res.users", "spouse_birthdate")
    util.remove_field(cr, "res.users", "children")
    util.remove_field(cr, "res.users", "visa_no")
    util.remove_field(cr, "res.users", "permit_no")
    util.remove_field(cr, "res.users", "certificate")
    util.remove_field(cr, "res.users", "study_field")
    util.remove_field(cr, "res.users", "study_school")
    util.remove_field(cr, "res.users", "hr_presence_state")
    util.remove_field(cr, "res.users", "last_activity")
    util.remove_field(cr, "res.users", "last_activity_time")
    util.remove_field(cr, "res.users", "employee_type")
    util.remove_field(cr, "res.users", "can_edit")

    util.create_column(cr, "hr_job", "user_id", "int4")
    util.move_field_to_module(cr, "hr.job", "user_id", "hr_recruitment", "hr")

    util.remove_menus(
        cr,
        [
            util.ref(cr, "hr.hr_menu_hr_task"),
            util.ref(cr, "hr.hr_menu_hr_my_activities"),
            util.ref(cr, "hr.hr_menu_hr_all_activities"),
            util.ref(cr, "hr.menu_hr_employee_user"),
            util.ref(cr, "hr.menu_hr_employee_contract_templates"),
        ],
    )
    util.remove_record(cr, "hr.action_hr_employee_my_activities")

    util.rename_xmlid(cr, "hr.contract_type_statutaire", "hr.contract_type_statutory", noupdate=True)

    util.create_column(cr, "hr_employee", "salary_distribution", "jsonb")
    util.explode_execute(
        cr,
        """
        UPDATE hr_employee e
            SET salary_distribution = jsonb_build_object(
                e.bank_account_id::text, jsonb_build_object(
                    'sequence', 1,
                    'amount', 100.0,
                    'amount_is_percentage', True
                )
            )
         WHERE e.bank_account_id IS NOT NULL
        """,
        table="hr_employee",
        alias="e",
    )

    util.convert_m2o_field_to_m2m(
        cr,
        "hr.employee",
        "bank_account_id",
        m2m_table="employee_bank_account_rel",
        col1="employee_id",
        col2="bank_account_id",
    )

    util.rename_field(cr, "res.users", "bank_account_id", "bank_account_ids")

    util.rename_field(cr, "res.users", "employee_bank_account_id", "employee_bank_account_ids")

    if util.module_installed(cr, "hr_payroll_account_iso20022"):
        util.move_field_to_module(
            cr,
            "hr.employee",
            "is_trusted_bank_account",
            "hr_payroll_account_iso20022",
            "hr",
        )

    util.rename_xmlid(cr, "hr.res_users_view_form_profile", "hr.res_users_view_form_preferences")
