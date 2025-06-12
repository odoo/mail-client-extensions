from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_recruitment_skills"):
        util.move_field_to_module(cr, "hr.job", "skill_ids", "hr_recruitment_skills", "hr_skill")
