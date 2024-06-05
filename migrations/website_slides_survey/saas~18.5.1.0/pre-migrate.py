from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_slides_survey.courses_home_inherit_survey")
