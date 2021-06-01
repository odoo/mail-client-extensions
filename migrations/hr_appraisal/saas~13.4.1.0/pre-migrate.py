# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Replaced by plans: Migrate Nothing
    util.remove_model(cr, "hr.appraisal.reminder")

    util.create_column(cr, "hr_job", "employee_feedback_template", "text")
    util.create_column(cr, "hr_job", "manager_feedback_template", "text")

    util.create_column(cr, "hr_appraisal", "employee_feedback", "text")
    util.create_column(cr, "hr_appraisal", "manager_feedback", "text")
    util.create_column(cr, "hr_appraisal", "employee_feedback_published", "boolean")
    util.create_column(cr, "hr_appraisal", "employee_manager_published", "boolean")

    util.create_column(cr, "res_company", "appraisal_plan", "boolean", default=True)
    util.create_column(cr, "res_company", "appraisal_employee_feedback_template", "text")
    util.create_column(cr, "res_company", "appraisal_manager_feedback_template", "text")
    util.create_column(cr, "res_company", "appraisal_confirm_employee_mail_template", "integer")
    util.create_column(cr, "res_company", "appraisal_confirm_manager_mail_template", "integer")

    # Coming from hr.employee.base
    util.create_column(cr, "hr_employee", "last_appraisal_id", "integer")

    # Remove noupdate data
    cr.execute(
        """
        DELETE FROM ir_config_parameter
        WHERE key IN ('hr_appraisal.appraisal_min_period', 'hr_appraisal.appraisal_max_period')
        """
    )
    removed_noupdate_data = """
        # activity types
        mail_act_appraisal_form
        mail_act_appraisal_send

        # config parameters
        config_appraisal_min_period
        config_appraisal_max_period

        # actions
        mail_activity_type_action_config_hr_appraisal
    """
    for removed_data in util.splitlines(removed_noupdate_data):
        util.delete_unused(cr, f"hr_appraisal.{removed_data}", deactivate=True)

    util.remove_view(cr, "hr_appraisal.mail_template_appraisal_reminder")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "hr_appraisal.menu_appraisal_reminder"),
            util.ref(cr, "hr_appraisal.hr_appraisal_menu_config_activity_type"),
        ],
    )

    # The action_plan (Char) old data could be moved to new field manager_feedback (Html)
    cr.execute("UPDATE hr_appraisal SET manager_feedback=%s" % util.pg_text2html("action_plan"))

    # company_id become a stored related field. Force recomputation be sure.
    cr.execute(
        """
            UPDATE hr_appraisal a
               SET company_id = e.company_id
              FROM hr_employee e
             WHERE e.id = a.employee_id
        """
    )

    all_fields_to_remove = {
        "res.users": """
            appraisal_colleagues_ids appraisal_by_colleagues appraisal_collaborators_ids
            appraisal_by_collaborators appraisal_self appraisal_manager_ids
            appraisal_by_manager""",
        "res.config.settings": """
            appraisal_by_colleagues_body_html appraisal_by_collaborators_body_html
            appraisal_by_employee_body_html appraisal_by_manager_body_html appraisal_by_colleagues
            appraisal_by_collaborators appraisal_by_employee appraisal_by_manager
            appraisal_send_reminder appraisal_max_period appraisal_min_period""",
        "hr.employee": """
            last_duration_reminder_send periodic_appraisal_created appraisal_collaborators_ids
            appraisal_by_collaborators appraisal_employee appraisal_self appraisal_colleagues_ids
            appraisal_by_colleagues appraisal_manager_ids appraisal_by_manager""",
        "hr.appraisal": """
            employee_body_html colleagues_body_html colleagues_ids action_plan is_autorized_to_send
            collaborators_body_html collaborators_ids manager_body_html manager_appraisal color""",
        "res.company": """
            appraisal_by_colleagues_body_html appraisal_by_collaborators_body_html
            appraisal_by_employee_body_html appraisal_by_manager_body_html appraisal_by_colleagues
            appraisal_by_collaborators appraisal_by_employee appraisal_by_manager appraisal_reminder
            appraisal_send_reminder""",
    }
    # Removed fields: Mostly overkill, nothing to do with existing data (yep, really :p)
    for model, fields_to_remove in all_fields_to_remove.items():
        for field_to_remove in fields_to_remove.split():
            util.remove_field(cr, model, field_to_remove)

    # Force noupdate data update
    util.update_record_from_xml(cr, "hr_appraisal.hr_appraisal_rule_base_user")
