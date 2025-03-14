from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_studio.default_form_page")
    util.remove_record(cr, "website_studio.action_web_studio_form")
