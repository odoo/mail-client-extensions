from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_dz.invoice_report_amount_in_words_inherit")

    cr.execute(
        """
        UPDATE res_company c
           SET display_invoice_amount_total_words = true
          FROM res_country t
         WHERE t.id = c.account_fiscal_country_id
           AND t.code = 'DZ'
        """
    )
