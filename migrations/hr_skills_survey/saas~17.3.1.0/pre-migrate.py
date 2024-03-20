from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE hr_resume_line AS resume_line
           SET date_end = NULL,
               expiration_status = 'valid'
          FROM survey_survey AS survey
         WHERE resume_line.survey_id = survey.id
           AND survey.certification = true
           AND resume_line.date_start = resume_line.date_end
        """,
        table="hr_resume_line",
        alias="resume_line",
    )
    util.explode_execute(
        cr,
        """
        WITH rld AS (
            SELECT resume_line.id, jsonb_object_agg(e.key, (CASE WHEN e.value::text = '"False"' THEN '""' ELSE to_json(e.value) END)) as description
              FROM hr_resume_line resume_line
              JOIN survey_survey s
                ON s.id = resume_line.survey_id
               AND resume_line.description::text LIKE '%"False"%'
                 , jsonb_each(resume_line.description) e
             WHERE s.certification = true
               AND {parallel_filter}
          GROUP BY resume_line.id
        )
        UPDATE hr_resume_line AS resume_line
           SET description = rld.description
          FROM rld
         WHERE rld.id = resume_line.id
        """,
        table="hr_resume_line",
        alias="resume_line",
    )
