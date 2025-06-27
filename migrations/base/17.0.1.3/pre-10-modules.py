from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "account_sepa_direct_debit_008_001_08", "account_sepa_direct_debit")
    util.force_upgrade_of_fresh_module(cr, "web_map")
    util.force_upgrade_of_fresh_module(cr, "l10n_ke_edi_oscu")
    util.force_upgrade_of_fresh_module(cr, "l10n_ke_edi_oscu_stock")
    util.force_upgrade_of_fresh_module(cr, "l10n_dk_bookkeeping")
    util.force_upgrade_of_fresh_module(cr, "l10n_cz_reports_2025")
    util.force_upgrade_of_fresh_module(cr, "l10n_ro_efactura")
    util.force_upgrade_of_fresh_module(cr, "l10n_in_ewaybill_stock")
