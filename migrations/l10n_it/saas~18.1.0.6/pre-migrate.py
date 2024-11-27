from psycopg2.sql import SQL

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        util.format_query(
            cr,
            """
            UPDATE account_tax
               SET invoice_legal_notes = {}
             WHERE l10n_it_law_reference IS NOT NULL
               AND invoice_legal_notes IS NULL
            """,
            SQL(util.pg_text2html("l10n_it_law_reference")),
        )
    )

    util.remove_field(cr, "account.tax", "l10n_it_law_reference")
