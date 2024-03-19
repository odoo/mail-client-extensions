from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_custom.custom_transaction_status", "payment_custom.custom_state_header")
