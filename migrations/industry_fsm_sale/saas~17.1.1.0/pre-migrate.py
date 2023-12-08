from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "product.product", "fsm_partner_price")
    util.remove_field(cr, "product.product", "fsm_partner_price_currency_id")
