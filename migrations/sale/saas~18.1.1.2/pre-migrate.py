from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.advance.payment.inv", "amount_to_invoice")
    util.remove_field(cr, "sale.advance.payment.inv", "display_invoice_amount_warning")
