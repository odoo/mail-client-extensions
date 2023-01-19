# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.applicant", "extract_can_show_resend_button")
    util.rename_field(cr, "hr.applicant", "is_first_stage", "is_in_extractable_state")
    util.rename_field(cr, "hr.applicant", "state_processed", "extract_state_processed")

    # remove metadata because it is now coming from the mixin
    util.remove_field_metadata(cr, "hr.applicant", "extract_can_show_send_button")
    util.remove_field_metadata(cr, "hr.applicant", "extract_error_message")
    util.remove_field_metadata(cr, "hr.applicant", "extract_remote_id")
    util.remove_field_metadata(cr, "hr.applicant", "extract_state")
    util.remove_field_metadata(cr, "hr.applicant", "extract_status_code")
    util.remove_field_metadata(cr, "hr.applicant", "extract_state_processed")

    # compute new fields
    util.create_column(cr, "hr_applicant", "is_in_extractable_state", "boolean", default=False)
    # simple case: no job_id
    query = "UPDATE hr_applicant SET is_in_extractable_state = true WHERE job_id IS NULL"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="hr_applicant"))
    # The CTE reimplement the search done in
    # https://github.com/odoo/enterprise/blob/ecea21ae609ecf5ea52b165a6a2f73b0bd4f65a5/hr_recruitment_extract/models/hr_applicant.py#L26-L30
    query = """
        WITH default_stage_by_job AS (
            SELECT j.id as job, l.id as stage
              FROM hr_job j
         LEFT JOIN lateral (
                 SELECT s.id
                   FROM hr_recruitment_stage s
              LEFT JOIN hr_job_hr_recruitment_stage_rel r
                     ON s.id = r.hr_recruitment_stage_id
                  WHERE r.hr_job_id IS NULL
                     OR r.hr_job_id = j.id
               ORDER BY s.sequence asc
                  FETCH FIRST ROW ONLY
                ) l
                ON true
        )
        UPDATE hr_applicant a
           SET is_in_extractable_state = true
          FROM default_stage_by_job j
         WHERE j.job = a.job_id
           AND j.stage IS NOT DISTINCT FROM a.stage_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="hr_applicant", alias="a"))
