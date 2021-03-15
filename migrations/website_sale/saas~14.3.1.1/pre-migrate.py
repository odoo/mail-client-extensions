from odoo.upgrade import util


def migrate(cr, version):

    # === IR UI VIEW ===#

    # Rename portal templates
    util.remove_view(cr, "website_sale.payment_sale_note")
