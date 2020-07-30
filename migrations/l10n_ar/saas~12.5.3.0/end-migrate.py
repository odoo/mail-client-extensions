# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
            UPDATE account_move m
               SET l10n_ar_currency_rate = 1.0
              FROM res_company c
             WHERE m.state = 'posted'
               AND m.l10n_ar_currency_rate IS NULL
               AND c.id = m.company_id
               AND c.currency_id = m.currency_id
        """
    )
