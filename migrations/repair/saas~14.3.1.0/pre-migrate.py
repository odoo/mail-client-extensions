# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "repair_order", "description", "varchar")
    util.create_column(cr, "repair_order", "sale_order_id", "int4")

    cr.execute("""
       UPDATE repair_order
          SET state = 'done'
        WHERE state = 'invoice_except'
    """)
