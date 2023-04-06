# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_m2m(cr, "hr_job_hr_recruitment_stage_rel", "hr_job", "hr_recruitment_stage")
    cr.execute(
        """
        INSERT INTO hr_job_hr_recruitment_stage_rel(hr_recruitment_stage_id, hr_job_id)
             SELECT id, job_id
               FROM hr_recruitment_stage
              WHERE job_id IS NOT NULL
    """
    )
    cr.execute(
        "UPDATE ir_ui_menu SET action = NULL WHERE id = %s",
        [util.ref(cr, "hr_recruitment.menu_crm_case_categ0_act_job")],
    )

    util.update_field_usage(cr, "hr.recruitment.stage", "job_id", "job_ids")
    util.remove_field(cr, "hr.recruitment.stage", "job_id")

    util.remove_field(cr, "hr.applicant", "reference")

    util.remove_view(cr, "hr_recruitment.view_crm_case_jobs_filter")
    util.remove_record(cr, "hr_recruitment.action_hr_job_no_employee")
    util.remove_record(cr, "hr_recruitment.hr_applicant_resumes")
    util.remove_record(cr, "hr_recruitment.menu_crm_case_categ0_act_job02")
