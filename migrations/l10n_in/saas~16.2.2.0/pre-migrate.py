from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_in.l10n_in_tcs_tds_view_partner_form")

    cr.execute(
        """
        UPDATE res_company c
           SET display_invoice_amount_total_words = true
          FROM res_country t
         WHERE t.id = c.account_fiscal_country_id
           AND t.code = 'IN'
        """
    )
