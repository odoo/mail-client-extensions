from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_ar_website_sale.address_b2b", "l10n_ar_website_sale.address")
