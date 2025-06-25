from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "account_sepa_direct_debit_008_001_08", "account_sepa_direct_debit")
    util.force_upgrade_of_fresh_module(cr, "web_map")
