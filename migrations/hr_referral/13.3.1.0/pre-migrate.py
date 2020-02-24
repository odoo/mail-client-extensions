# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_applicant", "last_valuable_stage_id", "int4")
    util.create_column(cr, "hr_recruitment_stage", "not_hired_stage", "boolean")

    cr.execute("UPDATE hr_recruitment_stage SET not_hired_stage = FALSE")
