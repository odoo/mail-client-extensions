# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # this script aims to detect and correct the database that would have been
    # a silent victim of the cogs lines post mig issue (from 12 to 13)

    if not util.module_installed(cr, "purchase_stock") or not util.version_between("14.0", "saas~15.1"):
        return

    cr.execute(
        """
        SELECT 1
          FROM account_move_line aml
         WHERE aml.is_anglo_saxon_line
         GROUP BY aml.move_id
        HAVING sum(aml.balance) != 0
         FETCH FIRST ROW ONLY
        """
    )
    if cr.rowcount == 0:
        return

    move_type = "move_type" if util.column_exists(cr, "account_move", "move_type") else "type"
    recompute_is_anglo_saxon_flag_for_all_aml(cr, move_type)


def recompute_is_anglo_saxon_flag_for_all_aml(cr, move_type):
    # the query works in several step:
    # 1. get the accounts relative to stock and price diff
    # 2. get income and expense accounts set on product and product category
    # 3. get all aml that are candidate to be an anglosaxon line
    # 4. get sure that for all candidate, there is an exact opposite one that isn't it-self (the balance = 0 corner case)
    # 5. compute the flag for all amls

    cr.execute(
        """
        WITH property_stock_account AS (
            -- ir_property.value_reference contains data like this "account.account,1020" which is "model,model.id"
            SELECT DISTINCT SUBSTRING(value_reference FROM '%,#"_*#"%' FOR '#')::int4
              FROM ir_property
             WHERE name IN (
                    'property_stock_account_input',
                    'property_stock_account_output',
                    'property_stock_account_input_categ_id',
                    'property_stock_account_output_categ_id',
                    'property_account_creditor_price_difference',
                    'property_account_creditor_price_difference_categ'
             )
        ),
        property_income_and_expense_account AS (
            SELECT DISTINCT SUBSTRING(value_reference FROM '%,#"_*#"%' FOR '#')::int4
              FROM ir_property
             WHERE name IN (
                    'property_account_income_id',
                    'property_account_expense_id',
                    'property_account_income_categ_id',
                    'property_account_expense_categ_id'
             )
        ),
        aml_candidate AS (
                SELECT aml.id,
                       aml.move_id,
                       aml.debit,
                       aml.credit
                  FROM account_move_line aml
            INNER JOIN account_move am     ON am.id = aml.move_id
            INNER JOIN account_account aa  ON aa.id = aml.account_id
            INNER JOIN product_product pp  ON pp.id = aml.product_id
            INNER JOIN product_template pt ON pt.id = pp.product_tmpl_id
                -- Those types are the only ones in which is_anglo_saxon_line is relevant
                 WHERE am.{move_type} IN ('in_invoice', 'in_refund', 'in_receipt', 'out_invoice', 'out_refund', 'out_receipt')
                   AND aml.exclude_from_invoice_tab
                   AND pt."type" ILIKE 'product'
                   AND aa.internal_type NOT IN ('receivable', 'payable')
                   AND (
                       aml.account_id IN (SELECT * FROM property_stock_account)
                       OR (
                        -- income and expense account are only relevant for out document
                        -- as 'in_document' only concerns stock and price diff account
                        am.{move_type} IN ('out_invoice', 'out_refund', 'out_receipt')
                        AND aml.account_id IN (SELECT * FROM property_income_and_expense_account)
                       )
                   )
        ),
        anglo_saxon_line_aml AS (
            SELECT ac1.id
              FROM aml_candidate ac1
                -- Every anglo_saxon_line is a line that has an exact counterpart in its own account_move
                -- ac1.id != ac2.id is there to avoid the lines with balance = 0 to match themselves
             WHERE EXISTS (
                   SELECT ac2.id
                     FROM aml_candidate ac2
                    WHERE ac1.move_id = ac2.move_id
                      AND ac1.debit = ac2.credit
                      AND ac1.credit = ac2.debit
                      AND ac1.id != ac2.id
             )
        ),
        all_aml AS (
            SELECT aml_original.id id,
                   -- compute the flag for every aml in the DB
                   (aml_original.id IN (SELECT id FROM anglo_saxon_line_aml)) AS computed_is_anglo_saxon_line
              FROM account_move_line aml_original
        )
        UPDATE account_move_line aml
           SET is_anglo_saxon_line = all_aml.computed_is_anglo_saxon_line
          FROM all_aml
         WHERE aml.id = all_aml.id
           AND aml.is_anglo_saxon_line IS DISTINCT FROM all_aml.computed_is_anglo_saxon_line
    """.format(
            move_type=move_type
        )
    )
