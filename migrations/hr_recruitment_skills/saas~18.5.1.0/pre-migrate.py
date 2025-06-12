from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_recruitment_skills.hr_job_form_inherit_hr_recruitment_skills")
