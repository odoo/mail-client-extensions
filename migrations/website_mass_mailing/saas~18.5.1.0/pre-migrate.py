from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_mass_mailing.newsletter_subscribe_options_common")
