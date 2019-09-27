# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util
from odoo import fields


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.account.saas-12.4." + __name__)


def _convert_to_account_move_vals(inv_vals):
    """ Convert fetched account_invoice vals / account_voucher vals to account_move vals
    in order to create missing account_move for draft / cancelled invoices.
    This is needed to migrate old invoices to handle the account-pocalypse feature.

    :param inv_vals:    A python dict.
    :return:            A python dict to be passed to ['account.move'].create
    """
    def fixup_array_agg(res):
        # Array_agg will return [None] if no result.
        if len(res) == 1 and res[0] is None:
            return []
        return res

    return {
        # Mandatory fields.
        "type": inv_vals["type"],
        "date": inv_vals["date"] or fields.Date.today(),
        "state": inv_vals["state"],
        "partner_id": inv_vals["partner_id"],
        "journal_id": inv_vals["journal_id"],
        "currency_id": inv_vals["currency_id"],
        "invoice_date": inv_vals["invoice_date"],
        # Optional fields.
        "ref": inv_vals.get("ref"),
        "narration": inv_vals.get("narration"),
        "fiscal_position_id": inv_vals.get("fiscal_position_id"),
        "invoice_partner_bank_id": inv_vals.get("invoice_bank_partner_id"),
        "invoice_cash_rounding_id": inv_vals.get("invoice_cash_rounding_id"),
        "invoice_date_due": inv_vals.get("invoice_date_due"),
        "invoice_incoterm_id": inv_vals.get("invoice_incoterm_id"),
        "invoice_origin": inv_vals.get("invoice_origin"),
        "invoice_payment_ref": inv_vals.get("invoice_payment_ref"),
        "invoice_payment_term_id": inv_vals.get("invoice_payment_term_id"),
        "invoice_sent": inv_vals.get("invoice_sent"),
        "invoice_source_email": inv_vals.get("invoice_source_email"),
        "invoice_user_id": inv_vals.get("invoice_user_id"),
        "invoice_vendor_display_name": inv_vals.get("invoice_vendor_display_name"),
        # Lines.
        "invoice_line_ids": [
            (0, 0, {
                "name": inv_line_vals["name"],
                "display_type": inv_line_vals.get("display_type"),
                "sequence": inv_line_vals["sequence"],
                "product_uom_id": inv_line_vals.get("product_uom_id"),
                "product_id": inv_line_vals["product_id"],
                "account_id": inv_line_vals["account_id"],
                "price_unit": inv_line_vals["price_unit"],
                "quantity": inv_line_vals["quantity"],
                "discount": inv_line_vals.get("discount"),
                "tax_ids": [(6, 0, [] if inv_line_vals.get("display_type") else fixup_array_agg(inv_line_vals["tax_ids"]))],
                "analytic_account_id": inv_line_vals["analytic_account_id"],
                "analytic_tag_ids": [(6, 0, fixup_array_agg(inv_line_vals["analytic_tag_ids"]))],
            })
            for inv_line_vals in inv_vals.get("invoice_line_ids", [])
        ],
    }


def _compute_invoice_line_move_line_mapping(cr):
    """ Compute the mapping between account_invoice_line and its corresponding account_move_line.
    :param cr:      The database cursor.
    :return:        A map <invoice_line_id> -> <account_move_line_id>.
    """

    _logger.info("compute invoice line move line mapping")
    is_account_voucher_installed = util.table_exists(cr, "account_voucher")

    # Create the mapping between account.invoice.line & account.move.line.
    cr.execute(
        """
        CREATE TABLE invl_aml_mapping (
            invl_id INTEGER NOT NULL,
            aml_id INTEGER NOT NULL,
            is_invoice_line BOOLEAN
        )
        """
    )

    query = """
        SELECT
            invl.id,
            'account_invoice_line' AS table,
            ARRAY_AGG(aml.id) AS candidates
        FROM account_invoice inv
        INNER JOIN res_company company ON company.id = inv.company_id
        INNER JOIN res_currency currency ON currency.id = inv.currency_id
        INNER JOIN account_move am ON am.id = inv.move_id
        LEFT JOIN account_invoice_line invl ON invl.invoice_id = inv.id
        LEFT JOIN account_move_line aml ON aml.move_id = am.id
        WHERE invl.display_type IS NULL
        AND inv.currency_id = am.currency_id
        AND invl.account_id = aml.account_id
        AND invl.product_id = aml.product_id
        AND invl.name = aml.name
        AND COALESCE(invl.account_analytic_id, 0) = COALESCE(aml.analytic_account_id, 0)	-- "null = null" is false in postgresql
        AND (
            (inv.currency_id = company.currency_id AND aml.currency_id IS NULL)
            OR
            (inv.currency_id != company.currency_id AND aml.currency_id = inv.currency_id)
        )
        AND (
            (inv.currency_id = company.currency_id AND ROUND(ABS(invl.price_subtotal) - ABS(aml.balance), currency.decimal_places) = 0.0)
            OR
            (inv.currency_id != company.currency_id AND ROUND(ABS(invl.price_subtotal) - ABS(aml.amount_currency), currency.decimal_places) = 0.0)
        )

        -- Equivalent of invl.tax_ids == aml.tax_ids in Python.
        AND (
            ARRAY(SELECT invl_tax.tax_id FROM account_invoice_line_tax invl_tax WHERE invl_tax.invoice_line_id = invl.id)
            @>
            ARRAY(SELECT aml_tax.account_tax_id FROM account_move_line_account_tax_rel aml_tax WHERE aml_tax.account_move_line_id = aml.id)
        )
        AND (
            ARRAY(SELECT invl_tax.tax_id FROM account_invoice_line_tax invl_tax WHERE invl_tax.invoice_line_id = invl.id)
            <@
            ARRAY(SELECT aml_tax.account_tax_id FROM account_move_line_account_tax_rel aml_tax WHERE aml_tax.account_move_line_id = aml.id)
        )

        -- Equivalent of invl.analytic_tag_ids == aml.analytic_tag_ids in Python.
        AND (
            ARRAY(SELECT invl_tag.account_analytic_tag_id FROM account_analytic_tag_account_invoice_line_rel invl_tag WHERE invl_tag.account_invoice_line_id = invl.id)
            @>
            ARRAY(SELECT aml_tag.account_analytic_tag_id FROM account_analytic_tag_account_move_line_rel aml_tag WHERE aml_tag.account_move_line_id = aml.id)
        )
        AND (
            ARRAY(SELECT invl_tag.account_analytic_tag_id FROM account_analytic_tag_account_invoice_line_rel invl_tag WHERE invl_tag.account_invoice_line_id = invl.id)
            <@
            ARRAY(SELECT aml_tag.account_analytic_tag_id FROM account_analytic_tag_account_move_line_rel aml_tag WHERE aml_tag.account_move_line_id = aml.id)
        )
        GROUP BY invl.id
    """
    if is_account_voucher_installed:
        query += """

            UNION ALL

            SELECT
                invl.id,
                'account_voucher_line' AS table,
                ARRAY_AGG(aml.id) AS candidates
            FROM account_voucher inv
            INNER JOIN res_company company ON company.id = inv.company_id
            INNER JOIN res_currency currency ON currency.id = inv.currency_id
            INNER JOIN account_move am ON am.id = inv.move_id
            LEFT JOIN account_voucher_line invl ON invl.voucher_id = inv.id
            LEFT JOIN account_move_line aml ON aml.move_id = am.id
            WHERE inv.currency_id = am.currency_id
            AND invl.account_id = aml.account_id
            AND invl.product_id = aml.product_id
            AND invl.name = aml.name
            AND COALESCE(invl.account_analytic_id, 0) = COALESCE(aml.analytic_account_id, 0)	-- "null = null" is false in postgresql
            AND (
                (inv.currency_id = company.currency_id AND aml.currency_id IS NULL)
                OR
                (inv.currency_id != company.currency_id AND aml.currency_id = inv.currency_id)
            )
            AND (
                (inv.currency_id = company.currency_id AND ROUND(ABS(invl.price_subtotal) - ABS(aml.balance), currency.decimal_places) = 0.0)
                OR
                (inv.currency_id != company.currency_id AND ROUND(ABS(invl.price_subtotal) - ABS(aml.amount_currency), currency.decimal_places) = 0.0)
            )

            -- Equivalent of invl.tax_ids == aml.tax_ids in Python.
            AND (
                ARRAY(SELECT invl_tax.account_tax_id FROM account_tax_account_voucher_line_rel invl_tax WHERE invl_tax.account_voucher_line_id = invl.id)
                @>
                ARRAY(SELECT aml_tax.account_tax_id FROM account_move_line_account_tax_rel aml_tax WHERE aml_tax.account_move_line_id = aml.id)
            )
            AND (
                ARRAY(SELECT invl_tax.account_tax_id FROM account_tax_account_voucher_line_rel invl_tax WHERE invl_tax.account_voucher_line_id = invl.id)
                <@
                ARRAY(SELECT aml_tax.account_tax_id FROM account_move_line_account_tax_rel aml_tax WHERE aml_tax.account_move_line_id = aml.id)
            )

            -- Equivalent of invl.analytic_tag_ids == aml.analytic_tag_ids in Python.
            AND (
                ARRAY(SELECT invl_tag.account_analytic_tag_id FROM account_analytic_tag_account_voucher_line_rel invl_tag WHERE invl_tag.account_voucher_line_id = invl.id)
                @>
                ARRAY(SELECT aml_tag.account_analytic_tag_id FROM account_analytic_tag_account_move_line_rel aml_tag WHERE aml_tag.account_move_line_id = aml.id)
            )
            AND (
                ARRAY(SELECT invl_tag.account_analytic_tag_id FROM account_analytic_tag_account_voucher_line_rel invl_tag WHERE invl_tag.account_voucher_line_id = invl.id)
                <@
                ARRAY(SELECT aml_tag.account_analytic_tag_id FROM account_analytic_tag_account_move_line_rel aml_tag WHERE aml_tag.account_move_line_id = aml.id)
            )
            GROUP BY invl.id
        """

    cr.execute("""
        WITH snuls AS (
            %s
        )
        INSERT INTO invl_aml_mapping(invl_id, aml_id, is_invoice_line)
        SELECT id, unnest(%s) aml_id, "table" = 'account_invoice_line'
          FROM snuls
    """ % (query, util.pg_array_uniq("candidates")))

    _logger.info("Indexing move lines mapping")
    cr.execute("create index on invl_aml_mapping(invl_id)")
    cr.execute("create index on invl_aml_mapping(aml_id)")
    cr.execute("create index on invl_aml_mapping(invl_id) WHERE is_invoice_line")
    cr.execute("create index on invl_aml_mapping(invl_id) WHERE not is_invoice_line")

    _logger.info("From account_invoice_line to account_move_line")
    # Copy business fields from account_invoice_line to account_move_line.
    with util.disable_triggers(cr, "account_move_line"):
        cr.execute(
            """
            UPDATE account_move_line aml
               SET quantity = invl.quantity,
                   price_unit = invl.price_unit,
                   discount = invl.discount,
                   price_subtotal = invl.price_subtotal,
                   price_total = invl.price_total
              FROM invl_aml_mapping mapping
        INNER JOIN account_invoice_line invl ON invl.id = mapping.invl_id
             WHERE mapping.is_invoice_line
               AND mapping.aml_id = aml.id
            """
        )
        if is_account_voucher_installed:
            # Copy business fields from account_voucher_line to account_move_line.
            cr.execute(
                """
                UPDATE account_move_line aml
                SET quantity = invl.quantity,
                    price_unit = invl.price_unit,
                    price_subtotal = invl.price_subtotal
                FROM invl_aml_mapping mapping
                JOIN account_voucher_line invl ON invl.id = mapping.invl_id
                WHERE NOT mapping.is_invoice_line AND mapping.aml_id = aml.id
                """
            )


def _save_fiscal_lock(cr):
    cr.execute("select id, tax_lock_date, period_lock_date, fiscalyear_lock_date INTO TEMPORARY TABLE res_company_saas124_acc_lock from res_company")
    cr.execute("UPDATE res_company SET tax_lock_date=NULL,period_lock_date=NULL,fiscalyear_lock_date=NULL")


def _retrieve_fiscal_lock(cr):
    cr.execute("""
        UPDATE res_company c
           SET tax_lock_date=s.tax_lock_date,
               period_lock_date=s.period_lock_date,
               fiscalyear_lock_date=s.fiscalyear_lock_date
          FROM res_company_saas124_acc_lock s
         WHERE s.id=c.id
    """)


def migrate(cr, version):
    env = util.env(cr)
    invoices_dict = {}
    is_account_voucher_installed = util.table_exists(cr, "account_voucher")
    _save_fiscal_lock(cr)

    # =======================================================================================
    # Migrate account_invoice to account_move
    # =======================================================================================

    # Create account_move for draft account_invoice.
    cr.execute(
        """
        SELECT
            inv.id,
            inv.currency_id,
            inv.date,
            inv.fiscal_position_id,
            inv.cash_rounding_id                    AS invoice_cash_rounding_id,
            inv.date_invoice                        AS invoice_date,
            inv.date_due                            AS invoice_date_due,
            inv.incoterm_id                         AS invoice_incoterm_id,
            inv.origin                              AS invoice_origin,
            inv.partner_bank_id                     AS invoice_bank_partner_id,
            inv.reference                           AS invoice_payment_ref,
            CASE WHEN inv.state = 'cancel' THEN 'cancel' ELSE 'draft' END
                                                    AS state,
            inv.payment_term_id                     AS invoice_payment_term_id,
            inv.sent                                AS invoice_sent,
            inv.source_email                        AS invoice_source_email,
            inv.user_id                             AS invoice_user_id,
            inv.vendor_display_name                 AS invoice_vendor_display_name,
            inv.journal_id,
            inv.name                                AS ref,
            inv.number                              AS name,
            inv.comment                             AS narration,
            inv.partner_id,
            inv.type
        FROM account_invoice inv
        WHERE inv.state IN ('draft', 'cancel')
    """
    )
    invoice_ids = []
    for inv_vals in cr.dictfetchall():
        invoices_dict["account_invoice," + str(inv_vals["id"])] = inv_vals
        invoice_ids.append(inv_vals["id"])
    if invoices_dict:
        # Manage account_invoice_line
        cr.execute(
            """
            SELECT
                inv_line.name,
                inv_line.display_type,
                inv_line.sequence,
                inv_line.invoice_id,
                inv_line.uom_id                     AS product_uom_id,
                inv_line.product_id,
                inv_line.account_id,
                inv_line.price_unit,
                inv_line.quantity,
                inv_line.discount,
                ARRAY_AGG(inv_line_tax.tax_id) AS tax_ids,
                inv_line.account_analytic_id        AS analytic_account_id,
                ARRAY_AGG(inv_line_tag.account_analytic_tag_id) AS analytic_tag_ids
            FROM account_invoice_line inv_line
            LEFT JOIN account_invoice_line_tax inv_line_tax ON inv_line_tax.invoice_line_id = inv_line.id
            LEFT JOIN account_analytic_tag_account_invoice_line_rel inv_line_tag ON inv_line_tag.account_invoice_line_id = inv_line.id
            WHERE inv_line.invoice_id IN %s
            GROUP BY
                inv_line.id,
                inv_line.name,
                inv_line.display_type,
                inv_line.sequence,
                inv_line.invoice_id,
                inv_line.uom_id,
                inv_line.product_id,
                inv_line.account_id,
                inv_line.price_unit,
                inv_line.quantity,
                inv_line.discount,
                inv_line.account_analytic_id
            ORDER BY inv_line.sequence, inv_line.id
        """,
            [tuple(invoice_ids)],
        )
        for inv_line_vals in cr.dictfetchall():
            key = "account_invoice," + str(inv_line_vals["invoice_id"])
            invoices_dict[key].setdefault("invoice_line_ids", [])
            invoices_dict[key]["invoice_line_ids"].append(inv_line_vals)

        # Manage account_invoice_tax
        cr.execute(
            """
            SELECT
                inv_tax.invoice_id,
                inv_tax.name,
                inv_tax.tax_repartition_line_id,
                inv_tax.amount
            FROM account_invoice_tax inv_tax
            WHERE inv_tax.invoice_id IN %s
        """,
            [tuple(invoice_ids)],
        )
        for inv_tax_vals in cr.dictfetchall():
            key = "account_invoice," + str(inv_tax_vals["invoice_id"])
            invoices_dict[key].setdefault("invoice_tax_ids", [])
            invoices_dict[key]["invoice_tax_ids"].append(inv_tax_vals)

    # =======================================================================================
    # Migrate account_voucher to account_move
    # =======================================================================================

    if is_account_voucher_installed:
        # Create account_move for draft account_voucher.
        cr.execute(
            """
            SELECT inv.id,
                   CASE WHEN inv.voucher_type = 'sale' THEN 'out_receipt' ELSE 'in_receipt' END
                                                       AS type,
                   inv.name                            AS ref,
                   inv.date                            AS invoice_date,
                   inv.date_due                        AS invoice_due_date,
                   inv.account_date                    AS date,
                   inv.journal_id,
                   inv.narration,
                   inv.currency_id,
                   inv.state,
                   inv.reference,
                   inv.partner_id
              FROM account_voucher inv
             WHERE inv.state IN ('draft', 'cancel')
        """
        )
        voucher_ids = []
        for inv_vals in cr.dictfetchall():
            invoices_dict["account_voucher," + str(inv_vals["id"])] = inv_vals
            voucher_ids.append(inv_vals["id"])
        if invoices_dict and voucher_ids:
            # Manage account_voucher_line
            cr.execute(
                """
                SELECT
                    inv_line.name,
                    inv_line.sequence,
                    inv_line.voucher_id AS invoice_id,
                    inv_line.product_id,
                    inv_line.account_id,
                    inv_line.price_unit,
                    inv_line.quantity,
                    ARRAY_AGG(inv_line_tax.account_tax_id) AS tax_ids,
                    inv_line.account_analytic_id AS analytic_account_id,
                    ARRAY_AGG(inv_line_tag.account_analytic_tag_id) AS analytic_tag_ids
                FROM account_voucher_line inv_line
                LEFT JOIN account_tax_account_voucher_line_rel inv_line_tax ON inv_line_tax.account_voucher_line_id = inv_line.id
                LEFT JOIN account_analytic_tag_account_invoice_line_rel inv_line_tag ON inv_line_tag.account_invoice_line_id = inv_line.id
                WHERE inv_line.voucher_id IN %s
                GROUP BY
                    inv_line.id,
                    inv_line.name,
                    inv_line.sequence,
                    inv_line.voucher_id,
                    inv_line.product_id,
                    inv_line.account_id,
                    inv_line.price_unit,
                    inv_line.quantity,
                    inv_line.account_analytic_id
                ORDER BY inv_line.sequence, inv_line.id
            """,
                [tuple(voucher_ids)],
            )
            for inv_line_vals in cr.dictfetchall():
                key = "account_voucher," + str(inv_line_vals["invoice_id"])
                invoices_dict[key].setdefault("invoice_line_ids", [])
                invoices_dict[key]["invoice_line_ids"].append(inv_line_vals)

    # =======================================================================================
    # Create missing account_moves
    # =======================================================================================
    _logger.info("Create missing account moves")

    # Create account_move
    created_moves = env["account.move"]
    invoices_list = list((k.split(",")[0], k.split(",")[1], v) for k, v in invoices_dict.items())
    for table, record_id, inv_vals in invoices_list:
        cr.execute("savepoint inv_creation_mig124")
        try:
            created_move = env["account.move"].with_context(check_move_validity=False).create(_convert_to_account_move_vals(inv_vals))
            created_moves |= created_move
            # Store link to newly created account_moves.
            cr.execute(
                "UPDATE %s SET move_id=%s WHERE id=%s" % (table, created_move.id, int(record_id))
            )
        except Exception:
            cr.execute("rollback to savepoint inv_creation_mig124")


    # =======================================================================================
    # Post fix account_moves
    # =======================================================================================

    _compute_invoice_line_move_line_mapping(cr)

    # Fix lines having display_type != False.
    _logger.info("Fix lines having display_type != False")
    if created_moves.ids:
        cr.execute(
            """
            UPDATE account_move_line aml_upd
               SET sequence=invoices.line_nb*10,
                   quantity=invoices.quantity,
                   price_unit=invoices.price_unit,
                   discount=invoices.discount,
                   price_subtotal=invoices.price_subtotal,
                   price_total=invoices.price_total
              FROM (
            SELECT invl.invoice_id,
                   invl.id,
                   invl.quantity,
                   invl.discount,
                   invl.price_unit,
                   invl.price_subtotal,
                   invl.price_total,
                   mapping.aml_id,
                   rank() over (PARTITION BY invl.invoice_id ORDER BY invl.invoice_id, invl.sequence, invl.id) as line_nb
            FROM account_invoice_line invl
      INNER JOIN account_invoice inv ON inv.id = invl.invoice_id
      INNER JOIN invl_aml_mapping mapping ON mapping.invl_id = invl.id AND mapping.is_invoice_line
           WHERE inv.move_id NOT IN %s
             AND invl.display_type IS NULL
        ORDER BY invl.invoice_id, invl.sequence, invl.id) AS invoices
           WHERE aml_upd.id=invoices.aml_id
            """, [tuple(created_moves.ids)]
        )

    # Fix lines having display_type != False.
    if created_moves.ids:
        cr.execute(
            """
            SELECT invl.invoice_id,
                   invl.id,
                   invl.display_type,
                   invl.name,
                   inv.move_id,
                   inv.currency_id,
                   comp.currency_id as company_currency_id
            FROM account_invoice_line invl
      INNER JOIN account_invoice inv ON inv.id = invl.invoice_id
      INNER JOIN res_company comp ON comp.id=inv.company_id
             AND inv.move_id NOT IN %s
             AND invl.display_type IS NOT NULL
        ORDER BY invl.invoice_id, invl.sequence, invl.id
            """, [tuple(created_moves.ids)]
        )

        create_todo = []
        for res in cr.dictfetchall():
            create_todo.append(
                {
                    "move_id": res["move_id"],
                    "name": res["name"],
                    "currency_id": res["currency_id"] != res["company_currency_id"] and res["currency_id"] or False,
                    "display_type": res["display_type"],
                }
            )

        if create_todo:
            env["account.move.line"].create(create_todo)

    with util.disable_triggers(cr, "account_move"):
        # Fix amount_untaxed, amount_untaxed_signed, amount_tax, amount_tax_signed, amount_total, amount_total_signed, amount_residual, amount_residual_signed.
        _logger.info("Fix amount_untaxed, amount_untaxed_signed, amount_tax, amount_tax_signed, amount_total, amount_total_signed, amount_residual, amount_residual_signed")
        cr.execute("""
            SELECT COALESCE(SUM(balance), 0.0) as amount, COALESCE(SUM(amount_currency), 0.0) as amount_curr, move_id
              INTO TEMPORARY TABLE am_untaxed
              FROM account_move_line
             WHERE tax_repartition_line_id IS NULL
               AND account_internal_type NOT IN ('receivable', 'payable')
          GROUP BY move_id
        """)
        cr.execute("""
            SELECT COALESCE(SUM(balance), 0.0) as amount, COALESCE(SUM(amount_currency), 0.0) as amount_curr, move_id
              INTO TEMPORARY TABLE am_tax
              FROM account_move_line
             WHERE tax_repartition_line_id IS NOT NULL
          GROUP BY move_id
        """)
        cr.execute("""
            SELECT COALESCE(SUM(balance), 0.0) as amount, COALESCE(SUM(amount_currency), 0.0) as amount_curr, move_id
              INTO TEMPORARY TABLE am_total
              FROM account_move_line
             WHERE account_internal_type NOT IN ('receivable', 'payable')
          GROUP BY move_id
        """)
        cr.execute("""
            SELECT COALESCE(SUM(amount_residual), 0.0) as amount, COALESCE(SUM(amount_residual_currency), 0.0) as amount_curr, move_id
              INTO TEMPORARY TABLE am_residual
              FROM account_move_line
             WHERE account_internal_type IN ('receivable', 'payable')
          GROUP BY move_id
        """)
        cr.execute("CREATE INDEX ON am_untaxed(move_id)")
        cr.execute("CREATE INDEX ON am_tax(move_id)")
        cr.execute("CREATE INDEX ON am_total(move_id)")
        cr.execute("CREATE INDEX ON am_residual(move_id)")

        _logger.info("Same currency as company")
        cr.execute(
            """
            -- ================ SINGLE-CURRENCY ================
            UPDATE account_move am
               SET amount_untaxed = am_untaxed.amount * (-1),
                   amount_untaxed_signed = am_untaxed.amount * (-1),
                   amount_tax = am_tax.amount * (-1),
                   amount_tax_signed = am_tax.amount * (-1),
                   amount_total = am_total.amount * (-1),
                   amount_total_signed = am_total.amount * (-1),
                   amount_residual = am_residual.amount,
                   amount_residual_signed = am_residual.amount
              FROM am_untaxed, am_tax, am_total, am_residual
             WHERE am.type IN ('out_invoice', 'out_receipt', 'in_refund')
               AND am.currency_id = am.company_currency_id
               AND am_untaxed.move_id=am.id
               AND am_tax.move_id=am.id
               AND am_total.move_id=am.id
               AND am_residual.move_id=am.id
            """
        )
        cr.execute(
            """
            UPDATE account_move am
               SET amount_untaxed = am_untaxed.amount,
                   amount_untaxed_signed = am_untaxed.amount * (-1),
                   amount_tax = am_tax.amount,
                   amount_tax_signed =  am_tax.amount * (-1),
                   amount_total = am_total.amount,
                   amount_total_signed = am_total.amount * (-1),
                   amount_residual = am_residual.amount,
                   amount_residual_signed = am_residual.amount
              FROM am_untaxed, am_tax, am_total, am_residual
             WHERE am.type IN ('in_invoice', 'in_receipt', 'out_refund')
               AND am.currency_id = am.company_currency_id
               AND am_untaxed.move_id=am.id
               AND am_tax.move_id=am.id
               AND am_total.move_id=am.id
               AND am_residual.move_id=am.id
            """
        )
        cr.execute(
            """
            UPDATE account_move am
               SET amount_untaxed = abs(am_untaxed.amount),
                   amount_untaxed_signed = abs(am_untaxed.amount),
                   amount_tax = abs(am_tax.amount),
                   amount_tax_signed = abs(am_tax.amount),
                   amount_total = abs(am_total.amount),
                   amount_total_signed = abs(am_total.amount),
                   amount_residual = abs(am_residual.amount),
                   amount_residual_signed = abs(am_residual.amount)
              FROM am_untaxed, am_tax, am_total, am_residual
             WHERE am.type = 'entry'
               AND (SELECT COUNT(aml.currency_id) FROM account_move_line aml WHERE aml.currency_id IS NOT NULL AND am.id = aml.move_id) != 1
               AND am.currency_id = am.company_currency_id
               AND am_untaxed.move_id=am.id
               AND am_tax.move_id=am.id
               AND am_total.move_id=am.id
               AND am_residual.move_id=am.id
            """
        )

        _logger.info("Other currency than company")
        cr.execute(
            """
            -- ================ MULTI-CURRENCIES ================
            UPDATE account_move am
               SET amount_untaxed = am_untaxed.amount_curr * (-1),
                   amount_untaxed_signed = am_untaxed.amount_curr * (-1),
                   amount_tax = am_tax.amount_curr * (-1),
                   amount_tax_signed = am_tax.amount_curr * (-1),
                   amount_total = am_total.amount_curr * (-1),
                   amount_total_signed = am_total.amount_curr * (-1),
                   amount_residual = am_residual.amount_curr,
                   amount_residual_signed = am_residual.amount_curr
              FROM am_untaxed, am_tax, am_total, am_residual
             WHERE am.type IN ('out_invoice', 'out_receipt', 'in_refund')
               AND am.currency_id != am.company_currency_id
               AND am_untaxed.move_id=am.id
               AND am_tax.move_id=am.id
               AND am_total.move_id=am.id
               AND am_residual.move_id=am.id
            """
        )
        cr.execute(
            """
            UPDATE account_move am
               SET amount_untaxed = am_untaxed.amount_curr,
                   amount_untaxed_signed = am_untaxed.amount_curr * (-1),
                   amount_tax = am_tax.amount_curr,
                   amount_tax_signed = am_tax.amount_curr * (-1),
                   amount_total = am_total.amount_curr,
                   amount_total_signed = am_total.amount_curr * (-1),
                   amount_residual = am_residual.amount_curr,
                   amount_residual_signed = am_residual.amount_curr
              FROM am_untaxed, am_tax, am_total, am_residual
             WHERE am.type IN ('in_invoice', 'in_receipt', 'out_refund')
               AND am.currency_id != am.company_currency_id
               AND am_untaxed.move_id=am.id
               AND am_tax.move_id=am.id
               AND am_total.move_id=am.id
               AND am_residual.move_id=am.id
            """
        )
        cr.execute(
            """
            UPDATE account_move am
               SET amount_untaxed = abs(am_untaxed.amount_curr),
                   amount_untaxed_signed = abs(am_untaxed.amount_curr),
                   amount_tax = abs(am_tax.amount_curr),
                   amount_tax_signed = abs(am_tax.amount_curr),
                   amount_total = abs(am_total.amount_curr),
                   amount_total_signed = abs(am_total.amount_curr),
                   amount_residual = abs(am_residual.amount_curr),
                   amount_residual_signed = abs(am_residual.amount_curr)
              FROM am_untaxed, am_tax, am_total, am_residual
             WHERE am.type = 'entry' AND (SELECT COUNT(aml.currency_id) FROM account_move_line aml WHERE aml.currency_id IS NOT NULL AND am.id = aml.move_id) = 1
               AND am.currency_id != am.company_currency_id
               AND am_untaxed.move_id=am.id
               AND am_tax.move_id=am.id
               AND am_total.move_id=am.id
               AND am_residual.move_id=am.id
        """
        )

        _logger.info("Fix invoice_payment_state.")
        cr.execute(
            """
            UPDATE account_move am
            SET invoice_payment_state = CASE WHEN ABS(am.amount_residual) < 0.0001 THEN 'paid' ELSE 'not_paid' END
            """
        )
        cr.execute(
            """
            UPDATE account_move am
            SET invoice_payment_state = 'in_payment'
            WHERE am.invoice_payment_state = 'paid'
            AND am.id IN (
                SELECT move.id
                FROM account_move move
                JOIN account_move_line line ON line.move_id = move.id
                JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                JOIN account_move_line rec_line ON
                    (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                    OR
                    (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                JOIN account_payment payment ON payment.id = rec_line.payment_id
                JOIN account_journal journal ON journal.id = rec_line.journal_id
                WHERE payment.state IN ('posted', 'sent')
                AND journal.post_at_bank_rec IS TRUE
            )
        """
        )

        _logger.info("Migrate refund_invoice_id => reversed_entry_id")
        cr.execute(
            """
            UPDATE account_move am
               SET reversed_entry_id = refund.move_id
              FROM account_invoice inv
        INNER JOIN account_invoice refund ON refund.id = inv.refund_invoice_id
             WHERE am.id=inv.move_id
        """
        )

        _logger.info("Migrate the chatter from account_invoice to account_move.")
        cr.execute(
            """
            -- mail_thread
            -- Fix added new stored 'message_main_attachment_id' field.
            UPDATE account_move am
            SET message_main_attachment_id = inv.message_main_attachment_id
            FROM account_invoice inv
            WHERE am.id = inv.move_id
            """
        )
    _retrieve_fiscal_lock(cr)
