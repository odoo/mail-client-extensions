# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_recruitment.group_hr_recruitment_interviewer")
    util.update_record_from_xml(cr, "hr_recruitment.group_hr_recruitment_user")
