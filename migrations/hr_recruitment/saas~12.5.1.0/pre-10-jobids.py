# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Missing removal in saas-9 for some dbs
    # See commit 239fa9b151834f8e31e196c4edd8a8bbc51e1080
    util.remove_field(cr, "hr.recruitment.stage", "job_ids")
    util.remove_field(cr, "hr.job", "stage_ids")
    cr.execute("DROP TABLE IF EXISTS job_stage_rel")
