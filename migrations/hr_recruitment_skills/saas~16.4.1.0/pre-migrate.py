# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_recruitment_skills.access_hr_applicant_skill")
