from odoo.upgrade import util


def disable_obsolete_tax_tag(cr, tag_xmlid):
    """
    Disable an obsolete tax tag by removing its associations and deactivating it.

    This method performs two major operations:
    1. Removes all associations between the given tax tag and tax repartition lines in the database.
    2. Deactivates the tax tag in the database if it is still used, otherwise removes it completely.

    Parameters:
    tag_xmlid (str): XMLID of the tax tag to be disabled.
    """
    tag_id = util.ref(cr, tag_xmlid)
    if tag_id:
        cr.execute(
            """
            DELETE FROM account_account_tag_account_tax_repartition_line_rel
             WHERE account_account_tag_id = %s
            """,
            [tag_id],
        )
        util.delete_unused(cr, tag_xmlid, deactivate=True)


def migrate(cr, version):
    disable_obsolete_tax_tag(cr, "l10n_mn.vat_report_tag43")

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
