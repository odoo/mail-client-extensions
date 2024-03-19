from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "payment_sepa_direct_debit.sepa_transaction_status", "payment_sepa_direct_debit.sepa_state_header"
    )
