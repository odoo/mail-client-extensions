# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE account_move_line aml
           SET  subscription_mrr = -1 * subscription_mrr
          FROM account_move AS am
         WHERE am.id=aml.move_id
           AND am.move_type = 'out_refund'
           AND aml.subscription_mrr > 0
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move_line", alias="aml"))
