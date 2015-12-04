# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'hr.applicant_category', 'hr.applicant.category', rename_table=False)

    util.create_m2m(cr, 'job_stage_rel', 'hr_job', 'hr_recruitment_stage', 'job_id', 'stage_id')
    cr.execute("""
        INSERT INTO job_stage_rel(job_id, stage_id)
        SELECT j.id, s.id
          FROM hr_job j
          JOIN hr_recruitment_stage s ON (s.department_id = j.department_id OR s.department_id IS NULL)
    """)

    # keep stages in case they are actually used
    for x in range(1, 7):
        util.force_noupdate(cr, 'hr_recruitment.stage_job%d' % x, True)
