from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_br_website_sale.portal_my_details_fields")
    util.remove_view(cr, "l10n_br_website_sale.address")
