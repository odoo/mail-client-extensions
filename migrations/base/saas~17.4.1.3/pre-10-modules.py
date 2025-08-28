from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "data_merge", "data_cleaning")
    util.merge_module(cr, "im_livechat_mail_bot", "mail_bot")
    util.force_upgrade_of_fresh_module(cr, "event_product", init=False)
    util.merge_module(cr, "l10n_cl_edi_boletas", "l10n_cl_edi")
    util.merge_module(cr, "account_audit_trail", "account")
    util.remove_module(cr, "l10n_de_audit_trail")
    util.merge_module(cr, "l10n_br_avatax_services", "l10n_br_avatax")
    util.merge_module(cr, "l10n_br_edi_services", "l10n_br_edi")
    util.merge_module(cr, "l10n_br_edi_sale_services", "l10n_br_edi_sale")
    util.merge_module(cr, "l10n_fr_invoice_addr", "l10n_fr_account")
    util.merge_module(cr, "l10n_ro_efactura", "l10n_ro_edi")

    if util.has_enterprise():
        util.merge_module(cr, "l10n_ch_hr_payroll_elm", "l10n_ch_hr_payroll")

    if util.module_installed(cr, "l10n_br") and not util.module_installed(cr, "base_address_extended"):
        util.force_upgrade_of_fresh_module(cr, "base_address_extended")
