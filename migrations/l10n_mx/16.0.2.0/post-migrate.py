# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Remove 1XXX tags with 'nature' field and replace them by 2 tags: one for debitor account and one for creditor account.

    tax_debit_id = util.ref(cr, "l10n_mx.tag_debit_balance_account")
    tax_credit_id = util.ref(cr, "l10n_mx.tag_credit_balance_account")

    for table_to_adapt in ("account_account", "account_account_template"):
        cr.execute(
            f"""
                WITH mx_account_with_tags AS (
                    SELECT
                        rel.{table_to_adapt}_id AS account_id,
                        ARRAY_AGG(tag.nature) AS tag_natures
                    FROM account_account_tag tag
                    JOIN {table_to_adapt}_account_tag rel ON rel.account_account_tag_id = tag.id
                    WHERE tag.nature IS NOT NULL
                    GROUP BY rel.{table_to_adapt}_id
                )
                INSERT INTO {table_to_adapt}_account_tag ({table_to_adapt}_id, account_account_tag_id)
                SELECT
                    mx_account_with_tags.account_id,
                    CASE WHEN mx_account_with_tags.tag_natures @> ARRAY[cast('A' AS varchar)] THEN %s ELSE %s END
                FROM mx_account_with_tags
                  ON CONFLICT DO NOTHING
            """,
            [tax_credit_id, tax_debit_id],
        )
    cr.execute(
        """
            DELETE FROM account_account_account_tag aaat
                  USING account_account_tag tag
                  WHERE aaat.account_account_tag_id = tag.id
                    AND tag.nature IS NOT NULL
        """
    )
    cr.execute("DELETE FROM account_account_tag WHERE nature IS NOT NULL")

    util.remove_column(cr, "account_account_tag", "nature")
