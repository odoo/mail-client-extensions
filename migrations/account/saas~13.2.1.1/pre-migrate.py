# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "sequence_id")
    util.remove_field(cr, "account.journal", "refund_sequence_id")
    util.remove_field(cr, "account.journal", "sequence_number_next")
    util.remove_field(cr, "account.journal", "refund_sequence_number_next")

    util.create_column(cr, "account_journal", "sequence_override_regex", "varchar")
    util.create_column(cr, "account_journal", "sale_activity_type_id", "int4")
    util.create_column(cr, "account_journal", "sale_activity_user_id", "int4")
    util.create_column(cr, "account_journal", "sale_activity_note", "text")

    util.create_column(cr, "account_move", "posted_before", "boolean")
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_move
                   SET posted_before = (state = 'posted' OR name != '/')
            """,
        ),
    )

    util.rename_field(cr, "account.move", "invoice_payment_state", "payment_state")
    util.remove_field(cr, "account.move", "invoice_partner_icon")
    util.remove_field(cr, "account.move", "invoice_sequence_number_next")
    util.remove_field(cr, "account.move", "invoice_sequence_number_next_prefix")

    util.create_column(cr, "account_move_line", "matching_number", "varchar")
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_move_line l
                   SET matching_number = f.name
                  FROM account_full_reconcile f
                 WHERE f.id = l.full_reconcile_id
                   AND l.matching_number IS NULL
            """,
            prefix="l.",
        ),
    )
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_move_line l
                   SET matching_number = 'P'
                  FROM account_partial_reconcile p
                 WHERE (p.credit_move_id = l.id OR p.debit_move_id = l.id)
                   AND l.matching_number IS NULL
            """,
            prefix="l.",
        ),
    )

    util.create_column(cr, "res_company", "account_opening_date", "date")
    cr.execute(
        """
        UPDATE res_company c
           SET account_opening_date = m.date
          FROM account_move m
         WHERE m.id = c.account_opening_move_id
    """
    )

    util.rename_field(cr, "account.invoice.report", "invoice_payment_state", "payment_state")
