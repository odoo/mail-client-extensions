# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Need sale_line_id on stock move instead of procurement.sale_line_id
    util.create_column(cr, 'stock_move', 'sale_line_id', 'int4')
    util.explode_execute(
        cr,
        """UPDATE stock_move sm
                SET sale_line_id = p.sale_line_id
                FROM procurement_order p WHERE sm.procurement_id = p.id
        """,
        table="stock_move",
        alias="sm",
    )
