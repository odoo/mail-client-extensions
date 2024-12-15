from odoo.upgrade import util


def migrate(cr, version):
    if util.ENVIRON.get("l10n_in_reports_gstr"):
        script = util.import_script("l10n_in/saas~18.2.2.0/pre-migrate.py")
        script._l10n_in_enable_feature(cr, "l10n_in_gst_efiling_feature")
    else:
        util.create_column(cr, "account_move", "l10n_in_gstr2b_reconciliation_status", "varchar", default="pending")

    util.remove_field(cr, "account.journal", "l10n_in_gstr_activate_einvoice_fetch")
    util.remove_model(cr, "l10n_in_withholding.tds.tcs.report.handler")
    util.remove_field(cr, "res.company", "l10n_in_gstr_gst_auto_refresh_token")
    util.remove_field(cr, "res.config.settings", "l10n_in_gstr_gst_auto_refresh_token")
    # Check for records with a selection field value of 'manual' or 'automatic' and enable the Fetch Vendor EDI feature
    # Note: Companies with the former value 'do_nothing' will not have this flag set,
    # as it indicates they do not intend to use the Fetch Vendor EDI feature.
    util.create_column(cr, "res_company", "l10n_in_fetch_vendor_edi_feature", "boolean")
    cr.execute("""
        UPDATE res_company company
           SET l10n_in_fetch_vendor_edi_feature = true
          FROM res_country country
         WHERE company.l10n_in_gstr_activate_einvoice_fetch IN ('manual', 'automatic')
           AND country.id = company.account_fiscal_country_id
           AND country.code = 'IN'
    """)
    util.change_field_selection_values(
        cr, "res.company", "l10n_in_gstr_activate_einvoice_fetch", {"do_nothing": "manual"}
    )

    if util.module_installed(cr, "l10n_in_edi_gstr"):
        util.move_field_to_module(
            cr, "l10n_in.gst.return.period", "gstr1_include_einvoice", "l10n_in_reports", "l10n_in_edi_gstr"
        )
    else:  # better be sure, shouldn't happen since the module is autoinstall from dependencies of the merged module l10n_in_reports_gstr
        util.remove_field(cr, "l10n_in.gst.return.period", "gstr1_include_einvoice")
