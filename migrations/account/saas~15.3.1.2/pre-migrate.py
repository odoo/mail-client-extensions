# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_payment", "amount_company_currency_signed", "numeric")
    query = """
        UPDATE account_payment ap
           SET amount_company_currency_signed =
                (CASE
                    WHEN ap.payment_type = 'outbound'
                    THEN -1
                    ELSE 1
                END)
                * am.amount_total_signed
          FROM account_move am
         WHERE ap.move_id = am.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_payment", alias="ap"))
