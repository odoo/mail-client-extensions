from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_ec_sale.address")
    util.remove_view(cr, "l10n_ec_sale.portal_my_details_fields")
    util.remove_view(cr, "l10n_ec_sale.partner_info")
