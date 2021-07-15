# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "hr.appraisal.plan")
    util.remove_field(cr, "hr.appraisal", "job_id")
    util.create_column(cr, "hr_appraisal", "note", "text")
    util.create_column(cr, "hr_appraisal", "previous_appraisal_id", "int4")
    cr.execute(
        """
        WITH previous_appraisal AS (
            SELECT id,
                   LAG(id) OVER (PARTITION BY employee_id ORDER BY date_close,id) AS prev
              FROM hr_appraisal WHERE state != 'cancel'
        )
        UPDATE hr_appraisal
           SET previous_appraisal_id = previous_appraisal.prev
          FROM previous_appraisal
         WHERE hr_appraisal.id = previous_appraisal.id
    """
    )

    util.create_column(cr, "hr_employee", "appraisal_count", "int4", default=0)
    cr.execute(
        """
        WITH counts AS (
                SELECT employee_id, count(*) as cnt
                  FROM hr_appraisal
              GROUP BY employee_id
               )
        UPDATE hr_employee e
           SET appraisal_count = c.cnt
          FROM counts c
         WHERE c.employee_id = e.id
    """
    )

    util.create_column(cr, "hr_appraisal", "employee_feedback_template", "text")
    util.create_column(cr, "hr_appraisal", "manager_feedback_template", "text")
    util.create_column(cr, "hr_appraisal", "show_templates", "boolean", default=False)
    util.create_column(cr, "hr_appraisal", "appraisal_plan_posted", "boolean", default=False)

    util.remove_field(cr, "hr.appraisal.goal", "text_description")

    util.create_column(cr, "hr_department", "custom_appraisal_templates", "boolean", default=False)
    util.create_column(cr, "hr_department", "employee_feedback_template", "text")
    util.create_column(cr, "hr_department", "manager_feedback_template", "text")
    cr.execute(
        """
        UPDATE hr_department
           SET employee_feedback_template = res_company.appraisal_employee_feedback_template,
               manager_feedback_template = res_company.appraisal_manager_feedback_template
          FROM res_company
         WHERE hr_department.company_id = res_company.id
    """
    )

    util.create_column(cr, "res_company", "duration_after_recruitment", "int4", default=6)
    util.create_column(cr, "res_company", "duration_first_appraisal", "int4", default=6)
    util.create_column(cr, "res_company", "duration_next_appraisal", "int4", default=12)
    util.rename_field(cr, "res.company", "appraisal_confirm_employee_mail_template", "appraisal_confirm_mail_template")
    util.remove_field(cr, "res.company", "appraisal_confirm_manager_mail_template")
    util.remove_field(cr, "res.company", "appraisal_plan_ids")

    util.remove_field(cr, "request.appraisal", "deadline")
    util.remove_field(cr, "request.appraisal", "attachment_ids")
    cr.execute("DROP TABLE hr_appraisal_mail_compose_message_ir_attachments_rel")
    util.remove_field(cr, "res.config.settings", "appraisal_confirm_manager_mail_template")
    util.remove_field(cr, "res.config.settings", "appraisal_confirm_employee_mail_template")

    util.remove_field(cr, "hr.job", "manager_feedback_template")
    util.remove_field(cr, "hr.job", "employee_feedback_template")
