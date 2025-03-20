from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Remove 1XXX tags with 'nature' field and replace them by 2 tags: one for debitor account and one for creditor account.
    env = util.env(cr)
    CoA = env.ref("l10n_mx.mx_coa")
    for company in env["res.company"].search([("chart_template_id", "=", CoA.id)]):
        CoA.generate_account_groups(company=company)

    tax_debit_id = util.ref(cr, "l10n_mx.tag_debit_balance_account")
    tax_credit_id = util.ref(cr, "l10n_mx.tag_credit_balance_account")

    for table_to_adapt in ("account_account", "account_account_template"):
        query = util.format_query(
            cr,
            """
                WITH mx_account_with_tags AS (
                    SELECT
                        rel.{column} AS account_id,
                        ARRAY_AGG(tag.nature) AS tag_natures
                    FROM account_account_tag tag
                    JOIN {table} rel ON rel.account_account_tag_id = tag.id
                    WHERE tag.nature IS NOT NULL
                    GROUP BY rel.{column}
                )
                INSERT INTO {table} ({column}, account_account_tag_id)
                SELECT
                    mx_account_with_tags.account_id,
                    CASE WHEN mx_account_with_tags.tag_natures @> ARRAY[cast('A' AS varchar)] THEN %s ELSE %s END
                FROM mx_account_with_tags
                  ON CONFLICT DO NOTHING
            """,
            table=f"{table_to_adapt}_account_tag",
            column=f"{table_to_adapt}_id",
        )
        cr.execute(query, [tax_credit_id, tax_debit_id])
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
