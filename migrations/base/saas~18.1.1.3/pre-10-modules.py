from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_us_hr_payroll_state_calculation", "l10n_us_hr_payroll")
    util.merge_module(cr, "l10n_in_reports_gstr_spreadsheet", "l10n_in_reports_gstr")
    util.merge_module(cr, "l10n_in_withholding_payment", "l10n_in_withholding")
    util.merge_module(cr, "auth_totp_mail_enforce", "auth_totp_mail")
    util.merge_module(cr, "l10n_es_modelo130", "l10n_es")
    util.rename_module(cr, "l10n_in_edi_ewaybill", "l10n_in_ewaybill")
    if util.has_enterprise():
        util.merge_module(cr, "l10n_nl_reports_sbr", "l10n_nl_reports")
        util.merge_module(cr, "l10n_nl_reports_sbr_ob_nummer", "l10n_nl_reports")
        util.merge_module(cr, "l10n_nl_reports_sbr_status_info", "l10n_nl_reports")
        util.merge_module(cr, "l10n_nl_reports_sbr_icp", "l10n_nl_reports")
        util.rename_module(cr, "pos_urban_piper_swiggy", "l10n_in_pos_urban_piper")
        util.merge_module(cr, "pos_urban_piper_zomato", "l10n_in_pos_urban_piper")
        util.merge_module(cr, "l10n_es_reports_modelo130", "l10n_es_reports")
        util.merge_module(cr, "l10n_ee_rounding", "l10n_ee_reports")
        if not util.version_gte("saas~18.2"):  # module reintroduced in 18.2
            util.remove_module(cr, "documents_account_peppol")
        util.merge_module(cr, "account_intrastat_services", "account_intrastat")
        util.merge_module(cr, "l10n_be_intrastat_services", "l10n_be_intrastat")
        util.merge_module(cr, "l10n_fr_intrastat_services", "l10n_fr_intrastat")
