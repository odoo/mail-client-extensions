# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_appraisal_skills.{hr_appraisal_skill_view_form,view_hr_appraisal_form}"))
