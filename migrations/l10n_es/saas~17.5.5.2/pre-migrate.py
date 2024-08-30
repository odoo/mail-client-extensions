from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "l10n_es_simplified_invoice_limit", "float8", default=400)
    if util.column_exists(cr, "pos_config", "l10n_es_simplified_invoice_limit"):
        cr.execute("""
            WITH limit_per_company(company_id, l10n_es_simplified_invoice_limit) AS (
                SELECT rc.id,
                       MIN(pc.l10n_es_simplified_invoice_limit)
                  FROM pos_config pc
                  JOIN res_company rc
                    ON pc.company_id = rc.id
                  JOIN res_partner rp
                    ON rc.partner_id = rp.id
                  JOIN res_country rcou
                    ON rp.country_id = rcou.id
                 WHERE rcou.code = 'ES'
                   AND pc.l10n_es_simplified_invoice_limit IS NOT NULL
              GROUP BY rc.id
            )
            UPDATE res_company rc
               SET l10n_es_simplified_invoice_limit = lpc.l10n_es_simplified_invoice_limit
              FROM limit_per_company lpc
             WHERE rc.id = lpc.company_id
        """)
