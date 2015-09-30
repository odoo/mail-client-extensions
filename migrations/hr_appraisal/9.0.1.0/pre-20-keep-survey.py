# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    keep = ["appraisal_form", "opinion_form"]

    # appraisal_form
    d = {1: 5, 2: 3, 3: 2, 4: 3, 5: 1}
    for p, s in d.items():
        keep.append('appraisal_%d' % p)
        for ss in range(1, s + 1):
            keep.append('appraisal_%d_%d' % (p, ss))

    # grid col/rows
    for i in range(1, 6):
        keep.append('acol_3_1_%d' % i)
        keep.append('acol_3_2_%d' % i)
        keep.append('arow_3_2_%d' % i)
        keep.append('opcol_2_1_%d' % i)
        keep.append('oprow_2_1_%d' % i)
        keep.append('opcol_2_2_%d' % i)
        keep.append('oprow_2_2_%d' % i)     # oprow_2_2_5 does not exists, but it does not matter
        keep.append('opcol_2_3_%d' % i)
        keep.append('oprow_2_3_%d' % i)     # again, no oprow_2_3_{4,5}
        keep.append('opcol_2_4_%d' % i)
        keep.append('oprow_2_4_%d' % i)     # no oprow_2_4_5
        keep.append('opcol_2_5_%d' % i)
        keep.append('oprow_2_5_%d' % i)     # no oprow_2_5_{3,4,5}
        keep.append('opcol_2_6_%d' % i)
        keep.append('oprow_2_6_%d' % i)     # no oprow_2_6_5

    for i in range(1, 16):
        keep.append('arow_3_1_%d' % i)

    # opinion_form
    d = {1: 2, 2: 7}
    for p, s in d.items():
        keep.append('opinion_%d' % p)
        for ss in range(1, s + 1):
            keep.append('opinion_%d_%d' % (p, ss))

    for k in keep:
        util.force_noupdate(cr, 'hr_appraisal.' + k, True)
