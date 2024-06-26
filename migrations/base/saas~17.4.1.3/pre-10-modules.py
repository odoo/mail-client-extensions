from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "data_merge", "data_cleaning")
    util.merge_module(cr, "im_livechat_mail_bot", "mail_bot")
    util.force_upgrade_of_fresh_module(cr, "event_product")
    util.merge_module(cr, "l10n_cl_edi_boletas", "l10n_cl_edi")
    util.merge_module(cr, "account_audit_trail", "account")
    util.remove_module(cr, "l10n_de_audit_trail")

    if util.has_enterprise():
        util.merge_module(cr, "l10n_ch_hr_payroll_elm", "l10n_ch_hr_payroll")
