from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_recruitment_skills"):
        util.move_field_to_module(cr, "hr.job", "skill_ids", "hr_recruitment_skills", "hr_skill")
    util.delete_unused(cr, "hr_skills.resume_type_social_media")
    util.remove_field(cr, "hr.resume.line", "display_type")
    util.create_column(cr, "hr_resume_line", "external_url", "varchar")
    util.create_column(cr, "hr_resume_line", "course_type", "varchar", default="external")
