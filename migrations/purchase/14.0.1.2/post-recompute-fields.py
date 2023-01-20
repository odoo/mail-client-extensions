# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.upgrade.util import inconsistencies


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

    inconsistencies.verify_uoms(cr, "purchase.order.line", uom_field="product_uom", ids=line_ids)
    inconsistencies.verify_products(
        cr,
        "purchase.order.line",
        "account.move.line",
        foreign_model_reference_field="purchase_line_id",
        ids=line_ids,
    )

    util.recompute_fields(cr, "purchase.order.line", ["qty_to_invoice"], ids=line_ids)
