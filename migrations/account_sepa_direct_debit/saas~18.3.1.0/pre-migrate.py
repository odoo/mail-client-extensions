from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "account_sepa_direct_debit.account_sepa_direct_debit_partner_mandates")
