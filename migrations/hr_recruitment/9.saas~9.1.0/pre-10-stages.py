# -*- coding: utf-8 -*-
import os
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'hr_recruitment_stage', 'job_id', 'int4')
    util.create_column(cr, 'hr_recruitment_stage', '_tmp', 'int4')
    cols = util.get_columns(cr, 'hr_recruitment_stage', ('id', 'job_id', '_tmp'))
    s_cols = ",".join("s." + c for c in cols)
    cols = ",".join(cols)

    cr.execute("""
        WITH only_one_job AS (
            SELECT stage_id, (array_agg(job_id))[1] as job_id
              FROM job_stage_rel
          GROUP BY 1
            HAVING count(job_id) = 1
        ),
        _ AS (
            DELETE FROM job_stage_rel r
                  USING only_one_job o
                  WHERE r.job_id=o.job_id
                    AND r.stage_id=o.stage_id
        )
        UPDATE hr_recruitment_stage s
           SET job_id = o.job_id
          FROM only_one_job o
         WHERE s.id = o.stage_id
    """)

    act = os.environ.get('ODOO_MIG_S9_JOB_STAGE', 'share')
    # 2 valid values: 'dup', 'share'

    if act == 'dup':
        cr.execute("""
            WITH stage_jobs AS (
                SELECT stage_id, array_agg(job_id order by job_id) as jobs
                  FROM job_stage_rel
              GROUP BY 1
                HAVING array_agg(job_id order by job_id) != (SELECT array_agg(id order by id) FROM hr_job)
            ),
            _upd AS (
              UPDATE hr_recruitment_stage s
                 SET job_id = t.jobs[1]
                FROM stage_jobs t
               WHERE t.stage_id = s.id
            ),
            new_stages AS (
                INSERT INTO hr_recruitment_stage({cols}, job_id, _tmp)
                     SELECT {s_cols}, unnest(t.jobs[2:array_length(t.jobs, 1)]), s.id
                       FROM hr_recruitment_stage s
                       JOIN stage_jobs t ON (s.id = t.stage_id)
                  RETURNING id, job_id, _tmp
            ),

            -- reassign applicants to correct stage depending on job
            -- users may seen duplicated stage in kanban view depending on applicant job
            _upd_applicant_stage AS (
                UPDATE hr_applicant l
                   SET stage_id = n.id
                  FROM new_stages n
                 WHERE l.stage_id = n._tmp
                   AND l.job_id = n.job_id
            )
            UPDATE hr_applicant l
               SET last_stage_id = n.id
              FROM new_stages n
             WHERE l.last_stage_id = n._tmp
               AND l.job_id = n.job_id
        """.format(**locals()))

    elif act != 'share':
        raise util.MigrationError('Invalid environment variable: $ODOO_MIG_S9_JOB_STAGE=%s' % act)

    util.remove_column(cr, 'hr_recruitment_stage', '_tmp')
    util.remove_field(cr, "hr.recruitment.stage", "job_ids")
    util.remove_field(cr, "hr.job", "stage_ids")
    cr.execute("DROP TABLE IF EXISTS job_stage_rel")
