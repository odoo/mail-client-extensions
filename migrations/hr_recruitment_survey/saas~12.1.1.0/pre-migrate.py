# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    xids = ["recruitment_form"]

    pages = {
        1: {1: 0, 2: 2, 3: 8},
        2: {1: 0, 2: 0, 3: 0, 4: 0},
        3: {1: 0},
    }
    for p in pages:
        xids.append("recruitment_{}".format(p))
        for x, y in pages[p].items():
            xids.append("recruitment_{}_{}".format(p, x))
            xids.extend(["recruitment_{}_{}_{}".format(p, x, z + 1) for z in range(y)])
    xids.extend(["rcol_3_1_{}".format(x + 1) for x in range(5)])
    xids.extend(["rrow_2_1_{}".format(x + 1) for x in range(13)])

    survey_id = util.ref(cr, "hr_recruitment_survey.recruitment_form")
    cr.execute("SELECT count(1) FROM survey_user_input_line WHERE survey_id=%s", [survey_id])
    if not cr.fetchone()[0]:
        for x in reversed(xids):
            util.remove_record(cr, "hr_recruitment_survey." + x)
    else:
        for x in xids:
            util.force_noupdate(cr, "hr_recruitment_survey." + x, True)
