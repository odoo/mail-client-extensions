# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.resume.line", "sequence")
    util.remove_field(cr, "hr.skill.level", "sequence")
    util.create_column(cr, "hr_resume_line", "display_type", "varchar")
    util.create_column(cr, "hr_resume_line_type", "sequence", "int4")
