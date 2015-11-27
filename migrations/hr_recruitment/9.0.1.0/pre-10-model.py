# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(cr, 'hr.applicant_category', 'hr.applicant.category', rename_table=False)

    # keep stages in case they are actually used
    for x in range(1, 7):
        util.force_noupdate(cr, 'hr_recruitment.stage_job%d' % x, True)
