from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_es_edi_tbai_multi_refund", "l10n_es_edi_tbai")
    util.merge_module(cr, "l10n_fr_reports_extended", "l10n_fr_reports")
    util.force_upgrade_of_fresh_module(cr, "account_bank_statement_extract")
