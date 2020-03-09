# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        WITH pos_account_templates AS (
           SELECT id, chart_template_id, code, user_type_id, reconcile
             FROM account_account_template
            WHERE id IN (SELECT default_pos_receivable_account_id FROM account_chart_template)
        ),
        matched_accounts AS (
            SELECT a.id, a.company_id, t.chart_template_id, 0 as ob
              FROM account_account a
              JOIN pos_account_templates t USING(code, user_type_id, reconcile)
             WHERE a.internal_type = 'receivable'

            UNION

            SELECT a.id, a.company_id, t.chart_template_id, 1 as ob
              FROM account_account a
              JOIN pos_account_templates t ON (
                        a.user_type_id = t.user_type_id
                    AND a.reconcile = t.reconcile
                    AND a.code LIKE CONCAT(substr(t.code, 0, length(t.code) - 1), '%')  -- s/%/_/ ?
              )
             WHERE a.internal_type = 'receivable'
        )
        UPDATE res_company c
           SET account_default_pos_receivable_account_id = (
                    SELECT id
                      FROM matched_accounts
                     WHERE company_id = c.id
                       AND chart_template_id = c.chart_template_id
                  ORDER BY ob, id
                     LIMIT 1
               )
         WHERE account_default_pos_receivable_account_id IS NULL
    """)

    cr.execute(
        """
        UPDATE pos_payment_method m
           SET receivable_account_id = c.account_default_pos_receivable_account_id
          FROM res_company c
         WHERE c.id = m.company_id
           AND m.receivable_account_id IS NULL
    """
    )
