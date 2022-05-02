# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def recompute_tax_audit_string(cr, aml_ids=None):
    q = """
  WITH tags AS (
          SELECT aml.id,
                 TRIM(LEADING FROM to_char((CASE WHEN t.tax_negate THEN -1 ELSE 1 END)
                                           *(CASE WHEN move.tax_cash_basis_rec_id IS NULL AND j.type = 'sale' THEN -1 ELSE 1 END)
                                           *(CASE WHEN move.tax_cash_basis_rec_id IS NULL AND (i.type IN ('in_refund', 'out_refund')
                                                                                               OR {pos_order_condition})
                                               THEN -1 ELSE 1 END)
                                           * aml.balance,
                                          '999,999,999,999,999,999,990.99')  -- should be enough, even for IRR
                 ) AS tag_amount,
                 cur.symbol AS currency,
                 cur.position AS cur_pos,
                 COALESCE(trl.tag_name, t.name) AS name
            FROM account_move_line aml
      INNER JOIN account_account_tag_account_move_line_rel t_rel ON t_rel.account_move_line_id = aml.id
      INNER JOIN account_account_tag t ON t.id = t_rel.account_account_tag_id
      INNER JOIN account_journal j ON j.id = aml.journal_id
      INNER JOIN account_move move ON move.id = aml.move_id
      INNER JOIN res_company c ON aml.company_id = c.id
      INNER JOIN res_currency cur ON c.currency_id = cur.id
       LEFT JOIN account_invoice i ON aml.move_id = i.move_id
       LEFT JOIN account_tax_report_line_tags_rel tr ON tr.account_account_tag_id = t.id
       LEFT JOIN account_tax_report_line trl ON tr.account_tax_report_line_id = trl.id
       {where_clause}
    ),
    tag_values AS (
        SELECT id,
               array_to_string(
                 array_agg(name || ': ' || CASE WHEN cur_pos = 'before' THEN   currency || ' ' || tag_amount
                                                ELSE                         tag_amount || ' ' || currency
                                                 END
                 ),
                 '        '
               ) AS tax_audit
          FROM tags
      GROUP BY id
  )
  UPDATE account_move_line
     SET tax_audit = tag_values.tax_audit
    FROM tag_values
   WHERE tag_values.id = account_move_line.id
    """.format(
        pos_order_condition="""(EXISTS(SELECT id
                                        FROM pos_order
                                       WHERE pos_order.account_move = aml.move_id)
                               AND i.id IS NULL
                               AND debit > 0
                              )"""
        if util.column_exists(cr, "pos_order", "account_move")
        else "false",
        where_clause="WHERE aml.id IN %s" if aml_ids else "WHERE {parallel_filter}",
    )
    if aml_ids:
        cr.execute(q, [tuple(aml_ids)])
    else:
        util.parallel_execute(cr, util.explode_query_range(cr, q, table="account_move_line", alias="aml"))


def migrate(cr, version):
    recompute_tax_audit_string(cr)
