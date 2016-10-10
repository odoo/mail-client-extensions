# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_field_to_module(cr, 'hr.job', 'survey_id', 'hr_recruitment', 'hr_recruitment_survey')
    util.move_field_to_module(cr, 'hr.applicant', 'survey_id', 'hr_recruitment', 'hr_recruitment_survey')
    util.move_field_to_module(cr, 'hr.applicant', 'response_id', 'hr_recruitment', 'hr_recruitment_survey')

    xids = ["recruitment_form"]

    survey = [
        [0, 2, 8],
        [0, 0, 0, 0],
        [0]
    ]
    for x, yz in enumerate(survey, 1):
        xids += ['recruitment_%d' % x]
        for y, z in enumerate(yz, 1):
            xy = 'recruitment_%d_%d' % (x, y)
            xids += [xy] + ['%s_%d' % (xy, zz) for zz in range(1, z)]

    xids += ['rcol_3_1_%d' % x for x in range(1, 6)]
    xids += ['rrow_2_1_%d' % x for x in range(1, 14)]

    for x in xids:
        util.rename_xmlid(cr, 'hr_recruitment.' + x, 'hr_recruitment_survey.' + x)
