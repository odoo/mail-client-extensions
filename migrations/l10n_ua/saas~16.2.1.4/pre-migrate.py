# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_company c
           SET display_invoice_amount_total_words = true
          FROM res_country t
         WHERE t.id = c.account_fiscal_country_id
           AND t.code = 'UA'
        """
    )
