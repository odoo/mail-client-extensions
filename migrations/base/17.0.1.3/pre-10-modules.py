from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "account_sepa_direct_debit_008_001_08", "account_sepa_direct_debit")
