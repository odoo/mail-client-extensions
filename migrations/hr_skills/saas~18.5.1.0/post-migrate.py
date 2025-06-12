from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_recruitment_skills"):
        cr.execute(
            """
       INSERT INTO hr_job_skill (
                       job_id, skill_id, skill_level_id, skill_type_id, valid_from
                   )
            SELECT rel.hr_job_id AS job_id,
                   rel.hr_skill_id AS skill_id,
                   (array_agg(
                       sl.id
                       ORDER BY
                           sl.default_level DESC NULLS LAST,  -- Prioritize default level
                           sl.level_progress ASC              -- Otherwise pick the lowest level
                   ))[1] AS skill_level_id,
                   s.skill_type_id,
                   COALESCE(MAX(hj.create_date), CURRENT_DATE) AS valid_from
              FROM hr_job_hr_skill_rel rel
              JOIN hr_skill s ON rel.hr_skill_id = s.id
         LEFT JOIN hr_job hj ON rel.hr_job_id = hj.id
         LEFT JOIN hr_skill_level sl ON s.skill_type_id = sl.skill_type_id
          GROUP BY rel.hr_job_id, rel.hr_skill_id, s.skill_type_id;
            """
        )
