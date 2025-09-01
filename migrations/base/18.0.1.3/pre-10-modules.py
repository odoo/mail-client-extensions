from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_es_edi_tbai_multi_refund", "l10n_es_edi_tbai")
    util.merge_module(cr, "l10n_fr_reports_extended", "l10n_fr_reports")
    util.force_upgrade_of_fresh_module(cr, "account_bank_statement_extract")

    if util.module_installed(cr, "l10n_sa_hr_payroll") and not util.module_installed(cr, "calendar"):
        # l10n_sa_hr_payroll now depends on hr_work_entry_holidays that depends (multi-level)
        # on calendar module, the latter adds a new column to res.partner
        util.create_column(cr, "res_partner", "calendar_last_notif_ack", "timestamp", default="now")

    if util.module_installed(cr, "l10n_bg"):
        # The new module l10n_bg_ledger is auto-installed from l10n_bg
        util.force_upgrade_of_fresh_module(cr, "l10n_bg_ledger")

    if util.module_installed(cr, "l10n_uk_bacs") and not util.module_installed(cr, "l10n_uk"):
        # situation that doesn't expect to be found outside CI.
        # `l10n_uk` will be installed after odoo/enterprise@147dafa3dcf4eff92b0379e14e589313a36d467e
        # which will install `base_vat`.
        util.ENVIRON["CI_IGNORE_NO_ORM_TABLE_CHANGE"].add(("res.partner", "vies_valid"))
