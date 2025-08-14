from odoo.upgrade import util


def migrate(cr, version):
    if util.modules_installed(cr, "account_budget"):
        util.force_install_module(cr, "account_budget_purchase")
    util.merge_module(cr, "l10n_be_reports_prorata", "l10n_be_reports")
    util.merge_module(cr, "account_edi_ubl_cii_tax_extension", "account_edi_ubl_cii")
    util.merge_module(cr, "l10n_be_hr_payroll_dmfa_sftp", "l10n_be_hr_payroll")
    util.merge_module(cr, "l10n_id_efaktur", "l10n_id_efaktur_coretax")
    util.force_upgrade_of_fresh_module(cr, "l10n_id_efaktur_coretax")
    util.remove_module(cr, "test_ai")
    util.merge_module(cr, "l10n_it_edi_withholding", "l10n_it_edi")
    util.rename_module(cr, "account_auto_transfer", "account_transfer")

    util.merge_module(cr, "pos_epson_printer", "point_of_sale")
    util.merge_module(cr, "pos_self_order_epson_printer", "pos_self_order")
