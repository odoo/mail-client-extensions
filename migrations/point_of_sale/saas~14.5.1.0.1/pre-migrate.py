# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "point_of_sale.qunit_suite_tests")
    util.remove_view(cr, "point_of_sale.report_invoice")
    util.remove_record(cr, "point_of_sale.pos_invoice_report")
    util.rename_field(cr, "pos.payment.method", "cash_journal_id", "journal_id")
    util.create_column(cr, "pos_payment_method", "type", "varchar")
    util.create_column(cr, "pos_payment_method", "outstanding_account_id", "integer")
    util.create_column(cr, "pos_payment", "account_move_id", "integer")
    util.create_column(cr, "account_payment", "pos_payment_method_id", "integer")
    util.create_column(cr, "account_payment", "pos_session_id", "integer")
    util.create_column(cr, "account_payment", "force_outstanding_account_id", "integer")

    cr.execute(
        """
        UPDATE pos_payment_method
           SET type = CASE is_cash_count WHEN true THEN 'cash' ELSE 'bank' END
    """
    )

    cr.execute(
        """
          WITH bank_journals as (
            SELECT company_id, min(id) as id
              FROM account_journal
             WHERE type = 'bank'
               AND active
          GROUP BY company_id
        )
        UPDATE pos_payment_method p
           SET journal_id = j.id
          FROM bank_journals j
         WHERE j.company_id = p.company_id
           AND p.type = 'bank'
    """
    )
