from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_enterprise.user_navbar")
    util.remove_view(cr, "website_enterprise.user_navbar_inherit_website_enterprise")
