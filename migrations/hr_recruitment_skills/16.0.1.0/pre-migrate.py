# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "hr_applicant_hr_skill_rel", "hr_applicant", "hr_skill")
    # This is a new module. There is no data to fill in this computed-store m2m.
