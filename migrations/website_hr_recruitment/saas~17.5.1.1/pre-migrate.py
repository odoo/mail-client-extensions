from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_hr_recruitment.hr_recruitment_source_kanban_inherit_website")
    util.remove_view(cr, "website_hr_recruitment.default_description")
