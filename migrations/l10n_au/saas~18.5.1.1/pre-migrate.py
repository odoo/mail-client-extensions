from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "l10n_au_is_gst_registered", "boolean")

    cr.execute(
        """
        UPDATE res_company c
           SET l10n_au_is_gst_registered = true
          FROM res_country r
         WHERE r.id = c.account_fiscal_country_id
           AND r.code = 'AU'
        """
    )
    util.add_to_migration_reports(
        "A new setting, <b>GST Registered</b>, has been introduced for Australian companies. "
        "It is enabled by default during the upgrade to preserve existing invoice behavior. "
        "Uncheck this option for non GST-registered companies to change the label from "
        "<b>Tax Invoice</b> to <b>Invoice</b> on your invoice PDFs.",
        category="Australian Accounting",
        format="html",
    )
