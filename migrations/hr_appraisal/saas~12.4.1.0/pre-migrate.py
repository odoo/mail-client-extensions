from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # models changes
    util.create_column(cr, "res_company", "appraisal_send_reminder", "boolean")

    for dest in {"manager", "collaborators", "colleagues", "employee"}:
        util.create_column(cr, "hr_appraisal", "{}_body_html".format(dest), "text")
        util.create_column(cr, "res_company", "appraisal_by_{}".format(dest), "boolean")
        util.create_column(cr, "res_company", "appraisal_by_{}_body_html".format(dest), "text")

        util.remove_field(cr, "hr.appraisal", "{}_survey_id".format(dest))
        util.remove_field(cr, "hr.employee", "appraisal_{}_survey_id".format(dest))
        util.remove_field(cr, "res.users", "appraisal_{}_survey_id".format(dest))

    util.remove_field(cr, "hr.appraisal", "survey_sent_ids")
    util.remove_field(cr, "hr.appraisal", "count_sent_survey")
    util.remove_field(cr, "hr.appraisal", "survey_completed_ids")
    util.remove_field(cr, "hr.appraisal", "count_completed_survey")
    util.remove_field(cr, "hr.appraisal", "survey_template_id")

    util.remove_field(cr, "hr.employee", "appraisal_self_survey_id")
    util.remove_field(cr, "res.users", "appraisal_self_survey_id")
    util.remove_field(cr, "res.users", "appraisal_employee")

    util.remove_field(cr, "survey.user_input", "appraisal_id")
    util.remove_field(cr, "survey.invite", "appraisal_id")

    # set default html message
    html = """
        <p>Please fill out the appraisal survey you received.<br/><br/>
        Thank you for your participation.</p>
    """

    cr.execute("""
        UPDATE res_company
           SET appraisal_send_reminder = true,
               appraisal_by_manager = true,
               appraisal_by_manager_body_html = %(html)s,
               appraisal_by_employee = true,
               appraisal_by_employee_body_html = %(html)s,
               appraisal_by_collaborators = false,
               appraisal_by_collaborators_body_html = %(html)s,
               appraisal_by_colleagues = false,
               appraisal_by_colleagues_body_html = %(html)s
    """, dict(html=html))

    cr.execute("""
        UPDATE hr_appraisal
           SET manager_body_html = %(html)s,
               employee_body_html = %(html)s,
               collaborators_body_html = %(html)s,
               colleagues_body_html = %(html)s
    """, dict(html=html))

    cr.execute("""
        UPDATE ir_act_server
           SET code = 'model.run_employee_appraisal()'
         WHERE id = (SELECT ir_actions_server_id FROM ir_cron WHERE id = %s)
    """, [util.ref(cr, "hr_appraisal.ir_cron_scheduler_appraisal")])

    # cleanup data
    util.remove_record(cr, "hr_appraisal.mail_template_user_input_appraisal")
    util.remove_record(cr, "hr_appraisal.access_calendar_attendee_survey_user")

    views = util.splitlines("""
        hr_appraisal_view_form_request
        res_config_settings_view_form
        survey_survey_view_form
        survey_user_input_view_search
        survey_user_input_view_form
        survey_view_kanban
        survey_invite_view_form
    """)
    for view in views:
        util.remove_view(cr, "hr_appraisal." + view)

    util.remove_column(cr, "hr_employee", "appraisal_employee")
