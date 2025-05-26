from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "l10n_ae_tax_report_counterpart_account")
    util.remove_field(cr, "res.config.settings", "l10n_ae_tax_report_counterpart_account")
    tag_id = util.ref(cr, "l10n_ae_reports.uae_account_tag_c_tax_cog")
    if tag_id:
        cr.execute(
            """
                DELETE FROM account_account_account_tag
                      WHERE account_account_tag_id = %s
            """,
            [tag_id],
        )
        util.remove_record(cr, "l10n_ae_reports.uae_account_tag_c_tax_cog")
