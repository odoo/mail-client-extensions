from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "is_edi_proxy_active")
    util.remove_field(cr, "res.config.settings", "l10n_it_edi_proxy_current_state")
    util.remove_field(cr, "res.config.settings", "l10n_it_edi_demo_mode")

    util.create_column(cr, "res_company", "l10n_it_edi_purchase_journal_id", "int4")
    cr.execute("""
        WITH to_update AS (
            SELECT child.id AS company_id,
                   -- collect journals taking first the journals of the closest parent
                   -- then the journal with minimum id among all that match
                   (ARRAY_AGG(
                       journal.id
                       ORDER BY ARRAY_POSITION(
                           STRING_TO_ARRAY(child.parent_path, '/'),
                           child.id::text
                       ) DESC, journal.id
                   ))[1] AS journal_id
              FROM res_company child
              JOIN res_company parent
                ON parent.id::text = ANY(STRING_TO_ARRAY(child.parent_path, '/'))
              JOIN account_journal journal
                ON journal.company_id = parent.id
              JOIN res_country child_country
                ON child_country.id = child.account_fiscal_country_id
              JOIN res_country parent_country
                ON parent_country.id = parent.account_fiscal_country_id
             WHERE child_country.code = 'IT'
               AND parent_country.code = 'IT'
               AND journal.type = 'purchase'
               AND journal.default_account_id IS NOT NULL
          GROUP BY child.id
        )
        UPDATE res_company company
           SET l10n_it_edi_purchase_journal_id = to_update.journal_id
          FROM to_update
         WHERE company.id = to_update.company_id
    """)
