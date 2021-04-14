# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.has_enterprise():
        util.new_module(cr, "hr_appraisal_skills", deps={"hr_appraisal", "hr_skills"}, auto_install=True)
