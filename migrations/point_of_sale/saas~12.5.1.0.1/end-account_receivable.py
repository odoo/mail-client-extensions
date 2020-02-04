# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE res_company c
           SET account_default_pos_receivable_account_id = act.default_pos_receivable_account_id
          FROM account_chart_template act
         WHERE c.chart_template_id=act.id
        """
    )
    cr.execute(
        """
        UPDATE pos_payment_method m
           SET receivable_account_id = c.account_default_pos_receivable_account_id
          FROM res_company c
         WHERE c.id = m.company_id
           AND m.receivable_account_id IS NULL
    """
    )
