# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

from odoo.tools import float_is_zero


def migrate(cr, version):
    env = util.env(cr)

    # Fix the amount_untaxed with anglo saxon lines.
    # If you make a purchase order to buy a product with a cost of 9 but you make the related vendor bill buying at a
    # cost of 12, an extra move line of 3 will be generated on the price difference account.
    # At this point of the migration, your account.move.line has price_unit=12 and credit=9 meaning the amount_untaxed
    # of the vendor bill is now wrong: amount_untaxed=9 because the total is based on the accounting values.

    # Also, the anglo saxon lines are removed when the vendor bill is reset to draft meaning Odoo will attempt to
    # unlink the original invoice line:

    #       account         |   price_unit  |   debit   |   credit  |   anglo-saxon flag    |
    # ---------------------------------------------------------------------------------------
    # stock input account   |          12.0 |       9.0 |           |                     t |   (invoice line)
    # price diff account    |               |       3.0 |           |                     t |

    # In order to fix the problem, we need to create an additional journal item containing the amount corresponding to
    # the price difference:

    #       account         |   price_unit  |   debit   |   credit  |   anglo-saxon flag    |
    # ---------------------------------------------------------------------------------------
    # stock input account   |          12.0 |      12.0 |           |                     f |   (invoice line)
    # stock input account   |               |           |       3.0 |                     t |
    # price diff account    |               |       3.0 |           |                     t |

    cr.execute('''
        SELECT
            move.type,
            move.currency_id AS move_currency_id,
            line.id,
            line.move_id,
            line.currency_id,
            line.account_id,
            line.company_currency_id,
            line.price_subtotal,
            line.amount_currency,
            line.balance,
            account.reconcile,
            anglo_line.id AS ang_id,
            anglo_line.name AS ang_name,
            anglo_line.partner_id AS ang_partner_id,
            anglo_line.partner_id AS ang_partner_id,
            anglo_line.product_id AS ang_product_id,
            anglo_line.product_uom_id AS ang_product_uom_id,
            anglo_line.quantity AS ang_quantity,
            anglo_line.price_unit AS ang_price_unit,
            anglo_line.price_subtotal AS ang_price_subtotal,
            anglo_line.analytic_account_id AS ang_analytic_account_id,
            ARRAY_AGG(analytic_rel.account_analytic_tag_id) AS ang_analytic_tag_ids,
            anglo_line.amount_currency AS ang_amount_currency,
            anglo_line.balance AS ang_balance,
            currency.decimal_places AS curr_decimal_places,
            comp_currency.decimal_places AS comp_curr_decimal_places
        FROM account_move_line line
        JOIN account_move move ON move.id = line.move_id
        JOIN account_account account ON account.id = line.account_id
        JOIN res_currency currency ON currency.id = move.currency_id
        JOIN res_currency comp_currency ON comp_currency.id = move.company_currency_id
        JOIN account_move_line anglo_line ON
            anglo_line.move_id = line.move_id
            AND anglo_line.is_anglo_saxon_line
            AND anglo_line.exclude_from_invoice_tab
            AND line.product_id = anglo_line.product_id
        LEFT JOIN account_analytic_tag_account_move_line_rel analytic_rel ON analytic_rel.account_move_line_id = anglo_line.id
        WHERE move.type IN ('in_invoice', 'in_refund', 'in_receipt')
        AND NOT line.exclude_from_invoice_tab
        GROUP BY
            move.type,
            move.currency_id,
            line.id,
            line.move_id,
            line.currency_id,
            line.account_id,
            line.company_currency_id,
            line.price_subtotal,
            line.amount_currency,
            line.balance,
            account.reconcile,
            anglo_line.id,
            anglo_line.name,
            anglo_line.partner_id,
            anglo_line.partner_id,
            anglo_line.product_id,
            anglo_line.product_uom_id,
            anglo_line.quantity,
            anglo_line.price_unit,
            anglo_line.price_subtotal,
            anglo_line.analytic_account_id,
            anglo_line.amount_currency,
            anglo_line.balance,
            currency.decimal_places,
            comp_currency.decimal_places            
    ''')

    to_write = {}
    processed_line_ids = set()
    to_unreconcile_line_ids = set()
    query_res = cr.dictfetchall()
    for res in query_res:
        if res['id'] in processed_line_ids or res['ang_id'] in processed_line_ids:
            continue

        factor = -1 if res['type'] == 'in_refund' else 1
        new_balance = res['balance'] + res['ang_balance']
        new_amount_currency = res['amount_currency'] + res['ang_amount_currency']

        if res['move_currency_id'] == res['company_currency_id']:

            if float_is_zero((res['price_subtotal'] * factor) - res['balance'], precision_digits=res['comp_curr_decimal_places']):
                continue

            if not float_is_zero((res['price_subtotal'] * factor) - res['balance'] - res['ang_balance'], precision_digits=res['comp_curr_decimal_places']):
                continue

        else:

            if float_is_zero((res['price_subtotal'] * factor) - res['amount_currency'], precision_digits=res['curr_decimal_places']):
                continue

            if not float_is_zero((res['price_subtotal'] * factor) - res['amount_currency'] - res['ang_amount_currency'], precision_digits=res['curr_decimal_places']):
                continue

        to_write.setdefault(res['move_id'], {'line_ids': []})

        to_write[res['move_id']]['line_ids'].append((1, res['id'], {
            'amount_currency': new_amount_currency,
            'debit': new_balance if new_balance > 0.0 else 0.0,
            'credit': -new_balance if new_balance < 0.0 else 0.0,
            'is_anglo_saxon_line': False,
        }))

        to_write[res['move_id']]['line_ids'].append((0, 0, {
            'name': res['ang_name'],
            'currency_id': res['currency_id'],
            'product_id': res['ang_product_id'],
            'product_uom_id': res['ang_product_uom_id'],
            'quantity': res['ang_quantity'],
            'price_unit': res['ang_price_unit'] or 0.0,
            'price_subtotal': res['ang_price_subtotal'],
            'account_id': res['account_id'],
            'analytic_account_id': res['ang_analytic_account_id'],
            'analytic_tag_ids': [(6, 0, [t for t in res['ang_analytic_tag_ids'] if t])],
            'amount_currency': res['ang_amount_currency'],
            'debit': -res['ang_balance'] if res['ang_balance'] < 0.0 else 0.0,
            'credit': res['ang_balance'] if res['ang_balance'] > 0.0 else 0.0,
            'exclude_from_invoice_tab': True,
            'is_anglo_saxon_line': True,
        }))

        processed_line_ids.add(res['id'])
        processed_line_ids.add(res['ang_id'])
        if res['reconcile']:
            to_unreconcile_line_ids.add(res['id'])

    if to_unreconcile_line_ids:
        env['account.move.line'].browse(list(to_unreconcile_line_ids)).remove_move_reconcile()
    for move_id, vals in to_write.items():
        env['account.move'].browse(move_id).write(vals)

    if to_write:
        cr.execute('''
            WITH with_amount_untaxed AS (
                SELECT
                    line.move_id,
                    CASE WHEN move.type = 'in_refund' THEN -1 ELSE 1 END AS factor,
                    SUM(line.amount_currency) AS amount_currency_untaxed,
                    SUM(line.balance) AS amount_untaxed
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                WHERE move.type IN ('in_invoice', 'in_refund', 'in_receipt')
                AND line.currency_id IS NOT NULL
                AND NOT line.exclude_from_invoice_tab
                AND line.move_id IN %s
                GROUP BY line.move_id, move.type
            )
            UPDATE account_move
            SET
                amount_untaxed = with_amount_untaxed.amount_currency_untaxed * with_amount_untaxed.factor,
                amount_untaxed_signed = with_amount_untaxed.amount_untaxed
            FROM with_amount_untaxed
            WHERE with_amount_untaxed.move_id = account_move.id
        ''', [tuple(to_write.keys())])

        cr.execute('''
            WITH with_amount_untaxed AS (
                SELECT
                    line.move_id,
                    CASE WHEN move.type = 'in_refund' THEN -1 ELSE 1 END AS factor,
                    SUM(line.balance) AS amount_untaxed
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                WHERE move.type IN ('in_invoice', 'in_refund', 'in_receipt')
                AND line.currency_id IS NULL
                AND NOT line.exclude_from_invoice_tab
                AND line.move_id IN %s
                GROUP BY line.move_id, move.type
            )
            UPDATE account_move
            SET
                amount_untaxed = with_amount_untaxed.amount_untaxed * with_amount_untaxed.factor,
                amount_untaxed_signed = with_amount_untaxed.amount_untaxed
            FROM with_amount_untaxed
            WHERE with_amount_untaxed.move_id = account_move.id
        ''', [tuple(to_write.keys())])
