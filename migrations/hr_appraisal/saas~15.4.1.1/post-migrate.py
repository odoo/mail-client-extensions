# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_appraisal.hr_appraisal_implicit_rule")
    util.update_record_from_xml(cr, "hr_appraisal.hr_appraisal_goal_own")
