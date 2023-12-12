from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "sale_down_payment_product_id")
    util.remove_field(cr, "res.config.settings", "deposit_default_product_id")
    util.remove_field(cr, "sale.advance.payment.inv", "product_id")
    util.remove_field(cr, "sale.advance.payment.inv", "deposit_account_id")
    util.remove_field(cr, "sale.advance.payment.inv", "deposit_taxes_id")
