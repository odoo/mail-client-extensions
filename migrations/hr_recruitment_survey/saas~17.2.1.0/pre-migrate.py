# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # hr_recruitment.group_hr_recruitment_interviewer shall not inherit
    # from survey.group_survey_user anymore
    query = """
        DELETE FROM res_groups_implied_rel
         WHERE gid = (
            SELECT res_id AS id
              FROM ir_model_data
             WHERE module = 'hr_recruitment'
               AND name = 'group_hr_recruitment_interviewer'
        )
          AND hid = (
            SELECT res_id AS id
              FROM ir_model_data
             WHERE module = 'survey'
               AND name = 'group_survey_user'
        )
    """
    cr.execute(query)

    # surveys linked to a job position should be of type 'recruitment'
    query = """
        WITH recruitment_survey AS (
            SELECT survey_id
              FROM hr_job
             WHERE survey_id IS NOT NULL
          GROUP BY survey_id
        )
        UPDATE survey_survey AS s
           SET survey_type = 'recruitment'
          FROM recruitment_survey AS rs
         WHERE s.id = rs.survey_id
    """

    cr.execute(query)
    if cr.rowcount:
        util.add_to_migration_reports(
            "Surveys linked to a Job position have been assigned the type 'recruitment'.", category="Survey"
        )
