from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "l10n_nl_rounding_difference_loss_account_id", "int4")
    util.create_column(cr, "res_company", "l10n_nl_rounding_difference_profit_account_id", "int4")

    cr.execute("""
        WITH accounts AS (
              SELECT min(rel.account_account_id) FILTER (WHERE p.value_text LIKE '4950%') AS profit_account_id,
                     min(rel.account_account_id) FILTER (WHERE p.value_text NOT LIKE '4950%') AS loss_account_id,
                     rel.res_company_id
                FROM account_account_res_company_rel rel
                JOIN res_company c
                  ON c.id = rel.res_company_id
                JOIN ir_property p
                  ON p.name = 'code'
                 AND p.res_id = 'account.account,' || rel.account_account_id
                 AND p.company_id = SPLIT_PART(c.parent_path, '/', 1)::int
               WHERE c.chart_template = 'nl'
                 AND p.value_text ~ '^49[56]0+$'
            GROUP BY rel.res_company_id
        )
        UPDATE res_company
           SET l10n_nl_rounding_difference_loss_account_id = accounts.profit_account_id,
               l10n_nl_rounding_difference_profit_account_id = accounts.loss_account_id
          FROM accounts
         WHERE accounts.res_company_id = res_company.id
    """)
