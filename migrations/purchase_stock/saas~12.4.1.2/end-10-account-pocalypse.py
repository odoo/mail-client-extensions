# -*- coding: utf-8 -*-

from odoo.tools import float_is_zero

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util.accounting import no_fiscal_lock


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

    # Note: during the migration, the taxes need to be fixed because the anglo saxon lines don't need taxes anymore.

    cr.execute(
        """
        WITH property_account AS (
            SELECT DISTINCT SUBSTRING(value_reference FROM '%,#"_*#"%' FOR '#')::int4 AS id
            FROM ir_property
            WHERE name IN (
                    'property_stock_account_input',
                    'property_stock_account_output',
                    'property_stock_account_input_categ_id',
                    'property_stock_account_output_categ_id',
                    'property_account_creditor_price_difference',
                    'property_account_creditor_price_difference_categ'
            )
        )
        UPDATE account_move_line
        SET is_anglo_saxon_line = 't'
        WHERE id IN (
            SELECT aml.id
            FROM account_move_line aml
            JOIN account_move move ON move.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN property_account prop_acc ON prop_acc.id = aml.account_id
            WHERE move.type IN ('in_invoice', 'in_refund', 'in_receipt')
            AND aml.product_id IS NOT NULL
            AND aml.tax_repartition_line_id IS NULL
            AND aml.display_type IS NULL
            AND aml.exclude_from_invoice_tab
            AND aa.internal_type NOT IN ('receivable', 'payable')
        )
    """
    )

    cr.execute(
        """
        SELECT
            CASE
                WHEN move.type = 'in_refund' THEN -1
                ELSE 1
            END AS factor,
            line.id,
            line.move_id,
            line.currency_id,
            line.account_id,
            line.price_subtotal,
            line.balance,
            account.reconcile,
            anglo_line.id AS ang_id,
            anglo_line.name AS ang_name,
            anglo_line.product_id AS ang_product_id,
            anglo_line.product_uom_id AS ang_product_uom_id,
            anglo_line.quantity AS ang_quantity,
            anglo_line.price_unit AS ang_price_unit,
            anglo_line.price_subtotal AS ang_price_subtotal,
            anglo_line.analytic_account_id AS ang_analytic_account_id,
            ARRAY_AGG(analytic_rel.account_analytic_tag_id) AS ang_analytic_tag_ids,
            anglo_line.amount_currency AS ang_amount_currency,
            anglo_line.balance AS ang_balance,
            (line.balance + anglo_line.balance) as new_balance,
            (line.amount_currency + anglo_line.amount_currency) as new_amount_currency,
            CASE
                WHEN move.currency_id = line.company_currency_id THEN line.balance
                ELSE line.amount_currency
            END AS balance_or_amount_currency,
            CASE
                WHEN move.currency_id = line.company_currency_id THEN anglo_line.balance
                ELSE anglo_line.amount_currency
            END AS ang_balance_or_ang_amount_currency,
            currency.decimal_places
        FROM account_move_line line
        JOIN account_move move ON move.id = line.move_id
        JOIN account_account account ON account.id = line.account_id
        JOIN res_currency currency ON currency.id = COALESCE(line.currency_id, line.company_currency_id)
        JOIN account_move_line anglo_line ON
            anglo_line.move_id = line.move_id
            AND anglo_line.is_anglo_saxon_line
            AND anglo_line.exclude_from_invoice_tab
            AND line.product_id = anglo_line.product_id
        LEFT JOIN account_analytic_tag_account_move_line_rel analytic_rel ON analytic_rel.account_move_line_id = anglo_line.id
        WHERE move.type IN ('in_invoice', 'in_refund', 'in_receipt')
        AND NOT line.exclude_from_invoice_tab
        AND line.display_type IS NULL
        GROUP BY
            move.type,
            move.currency_id,
            line.id,
            account.reconcile,
            anglo_line.id,
            currency.decimal_places
    """
    )

    to_write = {}
    processed_line_ids = set()
    to_unreconcile_line_ids = set()
    to_reconcile_line_ids = set()
    to_unlink_tax_line_ids = set()
    to_recompute_audit_string_line_ids = set()
    query_res = cr.dictfetchall()
    for res in query_res:
        if res["id"] in processed_line_ids or res["ang_id"] in processed_line_ids:
            continue

        price_sub_total_signed = res["price_subtotal"] * res["factor"]
        line_balance_currency = res["balance_or_amount_currency"]
        ang_balance_currency = res["ang_balance_or_ang_amount_currency"]

        is_balance_equals_to_price_subtotal = float_is_zero(
            price_sub_total_signed - line_balance_currency,
            precision_digits=res["decimal_places"],
        )
        if is_balance_equals_to_price_subtotal:
            continue

        is_balance_plus_ang_balance_equals_to_price_subtotal = float_is_zero(
            price_sub_total_signed - line_balance_currency - ang_balance_currency,
            precision_digits=res["decimal_places"],
        )
        if not is_balance_plus_ang_balance_equals_to_price_subtotal:
            continue

        to_unlink_tax_line_ids.add(res["ang_id"])
        to_recompute_audit_string_line_ids.add(res["id"])
        to_recompute_audit_string_line_ids.add(res["ang_id"])

        to_write.setdefault(res["move_id"], {"line_ids": []})

        to_write[res["move_id"]]["line_ids"].append(
            (
                1,
                res["id"],
                {
                    "amount_currency": res["new_amount_currency"],
                    "debit": res["new_balance"] if res["new_balance"] > 0.0 else 0.0,
                    "credit": -res["new_balance"] if res["new_balance"] < 0.0 else 0.0,
                    "is_anglo_saxon_line": False,
                },
            )
        )

        to_write[res["move_id"]]["line_ids"].append(
            (
                0,
                0,
                {
                    "name": res["ang_name"],
                    "currency_id": res["currency_id"],
                    "product_id": res["ang_product_id"],
                    "product_uom_id": res["ang_product_uom_id"],
                    "quantity": res["ang_quantity"],
                    "price_unit": res["ang_price_unit"] or 0.0,
                    "price_subtotal": res["ang_price_subtotal"],
                    "account_id": res["account_id"],
                    "analytic_account_id": res["ang_analytic_account_id"],
                    "analytic_tag_ids": [(6, 0, [t for t in res["ang_analytic_tag_ids"] if t])],
                    "amount_currency": -res["ang_amount_currency"],
                    "debit": -res["ang_balance"] if res["ang_balance"] < 0.0 else 0.0,
                    "credit": res["ang_balance"] if res["ang_balance"] > 0.0 else 0.0,
                    "exclude_from_invoice_tab": True,
                    "is_anglo_saxon_line": True,
                },
            )
        )

        processed_line_ids.add(res["id"])
        processed_line_ids.add(res["ang_id"])
        if res["reconcile"]:
            to_unreconcile_line_ids.add(res["id"])

    # ============================================================
    # Fix taxes on anglo-saxon lines that are not needed anymore
    # ============================================================

    if to_unlink_tax_line_ids:
        cr.execute(
            """
            DELETE FROM account_move_line_account_tax_rel rel
            WHERE rel.account_move_line_id IN %s
        """,
            [tuple(to_unlink_tax_line_ids)],
        )
        cr.execute(
            """
            DELETE FROM account_account_tag_account_move_line_rel rel
            USING account_account_tag tag
            WHERE rel.account_move_line_id IN %s AND tag.id = rel.account_account_tag_id AND tag.applicability = 'taxes'
        """,
            [tuple(to_unlink_tax_line_ids)],
        )

    # ============================================================
    # Fix journal items in order to fix the anglo saxon lines
    # ============================================================

    if to_unreconcile_line_ids:
        to_unreconcile_line = env["account.move.line"].browse(list(to_unreconcile_line_ids))
        for line in to_unreconcile_line:
            to_reconcile_line_ids.add(
                line + line.matched_debit_ids.debit_move_id + line.matched_credit_ids.credit_move_id
            )
        to_unreconcile_line.remove_move_reconcile()

    with no_fiscal_lock(cr):
        for move_id, vals in to_write.items():
            env["account.move"].browse(move_id).write(vals)

    # Again reconciled lines that unreconciled before.
    for lines in to_reconcile_line_ids:
        lines.filtered(lambda l: not l.reconciled).reconcile()

    # Ensure 'balance' is well computed in following queries.
    env["account.move"].flush()

    # ============================================================
    # Fix tax audit string since taxes are different.
    # ============================================================

    m = util.import_script("account/saas~12.3.1.1/end-20-recompute.py")
    if to_recompute_audit_string_line_ids:
        m.recompute_tax_audit_string(cr, aml_ids=to_recompute_audit_string_line_ids)

    # ============================================================
    # Fix amount_untaxed
    # ============================================================

    if to_write:
        cr.execute(
            """
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
        """,
            [tuple(to_write.keys())],
        )

        cr.execute(
            """
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
        """,
            [tuple(to_write.keys())],
        )
