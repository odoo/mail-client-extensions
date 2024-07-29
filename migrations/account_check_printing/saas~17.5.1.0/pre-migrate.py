from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_check_printing.view_partner_property_form")
    util.remove_view(cr, "account_check_printing.view_account_invoice_filter")
    util.remove_field(cr, "account.move", "preferred_payment_method_id")
    util.remove_field(cr, "res.partner", "property_payment_method_id")
