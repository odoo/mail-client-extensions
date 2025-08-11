from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_recruitment_skills"):
        util.move_field_to_module(cr, "hr.job", "skill_ids", "hr_recruitment_skills", "hr_skill")
    util.delete_unused(cr, "hr_skills.resume_type_social_media")
    util.remove_field(cr, "hr.resume.line", "display_type")
    util.remove_field(cr, "res.users", "resume_line_ids")
    util.remove_field(cr, "res.users", "employee_skill_ids")
    util.remove_field(cr, "res.users", "current_employee_skill_ids")
    util.remove_field(cr, "res.users", "certification_ids")
    util.remove_view(cr, "hr_skills.res_users_view_form")
    util.create_column(cr, "hr_resume_line", "external_url", "varchar")
    util.create_column(cr, "hr_resume_line", "course_type", "varchar", default="external")
