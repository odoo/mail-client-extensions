# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_analytic_line", "order_id", "int4")

    cr.execute("""
        UPDATE account_analytic_line l
           SET order_id = sol.order_id
          FROM sale_order_line sol
         WHERE sol.id = l.so_line
    """)
