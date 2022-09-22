# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT line.id
          FROM purchase_order_line line
          JOIN purchase_order po
            ON line.order_id = po.id
          JOIN product_product p
            ON line.product_id = p.id
          JOIN product_template pt
            ON p.product_tmpl_id = pt.id
         WHERE pt.purchase_method = 'purchase'
           AND po.state IN ('purchase', 'done')
        """
    )
    line_ids = [id[0] for id in cr.fetchall()]
    util.recompute_fields(cr, "purchase.order.line", ["qty_to_invoice"], ids=line_ids)
