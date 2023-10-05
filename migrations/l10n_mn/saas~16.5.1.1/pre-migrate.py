from odoo.upgrade import util


def migrate(cr, version):
    # VAT report migration: remove obsolete tag vat_report_tag43 from tax repartition lines.
    # If it is used on AMLs, remove its xmlid (so it won't be deleted), and set it to active=False.
    vat_report_tag43_id = util.ref(cr, "l10n_mn.vat_report_tag43")
    if vat_report_tag43_id:
        cr.execute(
            """
            DELETE FROM account_account_tag_account_tax_repartition_line_rel
                WHERE account_account_tag_id = %s
            """,
            [vat_report_tag43_id],
        )
        cr.execute(
            """
            SELECT tag_aml_rel.account_move_line_id
              FROM account_account_tag_account_move_line_rel tag_aml_rel
             WHERE tag_aml_rel.account_account_tag_id = %s
             LIMIT 1
            """,
            [vat_report_tag43_id],
        )
        if cr.fetchall():
            cr.execute(
                """
                DELETE FROM ir_model_data
                      WHERE module = 'l10n_mn'
                            AND model = 'account.account.tag'
                            AND res_id = %s
                """,
                [vat_report_tag43_id],
            )
            cr.execute(
                """
                UPDATE account_account_tag
                   SET active = false
                 WHERE id = %s
                """,
                [vat_report_tag43_id],
            )

    # Corporate Tax Report / Cashflow Statement: remove from accounts all account tags to be deleted
    cr.execute(
        r"""
        DELETE FROM account_account_account_tag aaat
              USING account_account_tag
               JOIN ir_model_data
                 ON ir_model_data.module = 'l10n_mn'
                    AND ir_model_data.model = 'account.account.tag'
                    AND ir_model_data.res_id = account_account_tag.id
              WHERE aaat.account_account_tag_id = account_account_tag.id
                    AND (
                        ir_model_data.name LIKE 'tax\_report\_tag%'
                        OR ir_model_data.name LIKE 'account\_tag\_operating\_%'
                        OR ir_model_data.name LIKE 'account\_tag\_investing\_%'
                        OR ir_model_data.name LIKE 'account\_tag\_financing\_%'
                        OR ir_model_data.name IN ('account_tag_exchange', 'vat_report_tag58', 'vat_report_tag59')
                    )
        """
    )

    # Delete the old tax report to avoid report line code clashes
    # (needs to be done before the new data in l10n_mn gets loaded)
    util.remove_record(cr, "l10n_mn_reports.account_report_vat_report")
