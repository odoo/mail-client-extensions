# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE account_move am
           SET amount_residual = 0,
               amount_residual_signed = 0
         WHERE am.state in ('draft', 'cancel')
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move", alias="am"))
