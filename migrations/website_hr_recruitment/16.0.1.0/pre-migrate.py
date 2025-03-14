from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_hr_recruitment.job_edit_options")
    util.remove_view(cr, "website_hr_recruitment.user_navbar_inherit_website_hr_recruitment")

    util.create_column(cr, "hr_job", "job_details", "text", default="")
