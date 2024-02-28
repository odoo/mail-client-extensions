# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE account_move_line line
           SET exclude_from_invoice_tab = 't'
          FROM account_account aa
          JOIN account_account_type aat
            ON aa.user_type_id = aat.id
         WHERE line.account_id = aa.id
           AND line.expense_id IS NOT NULL
           AND aat.type IN ('receivable', 'payable')
    """
    util.explode_execute(cr, query, table="account_move_line", alias="line")
