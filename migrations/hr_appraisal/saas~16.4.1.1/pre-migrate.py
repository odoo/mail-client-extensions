# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.appraisal.goal", "is_implicit_manager")
    util.remove_field(cr, "hr.appraisal", "is_appraisal_manager")
    util.remove_field(cr, "hr.appraisal", "is_implicit_manager")
    util.if_unchanged(cr, "hr_appraisal.hr_appraisal_emp_rule", util.update_record_from_xml)
