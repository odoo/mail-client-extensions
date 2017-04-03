# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'print.order.wizard', 'currency_id')
    util.create_column(cr, 'print_order_wizard', 'res_model', 'varchar')
    cr.execute("""
        UPDATE print_order_wizard w
           SET res_model = l.res_model
          FROM print_order_line_wizard l
         WHERE l.print_order_wizard_id = w.id
    """)

    util.remove_field(cr, 'print.order.line.wizard', 'res_model')
    util.remove_field(cr, 'print.order.line.wizard', 'state')
