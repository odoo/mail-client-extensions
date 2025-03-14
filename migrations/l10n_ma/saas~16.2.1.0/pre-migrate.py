from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_ma.l10n_kzc_temp_chart", "l10n_ma.l10n_ma_chart_template")

    cr.execute(
        """
        UPDATE res_company c
           SET display_invoice_amount_total_words = true
          FROM res_country t
         WHERE t.id = c.account_fiscal_country_id
           AND t.code = 'MA'
        """
    )
