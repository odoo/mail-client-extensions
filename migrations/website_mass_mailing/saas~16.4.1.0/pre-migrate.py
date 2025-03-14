from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_mass_mailing.iframe_css_assets_edit")
