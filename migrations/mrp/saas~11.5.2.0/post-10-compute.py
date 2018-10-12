# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Compute as much as possible using SQL
    cr.execute(
        """
        UPDATE mrp_production m
        SET product_uom_qty=product_qty
        FROM product_product p INNER JOIN product_template pt ON p.product_tmpl_id=pt.id
        WHERE pt.uom_id=m.product_uom_id
        AND m.product_id=p.id
    """
    )
    # Then let ORM compute remaining records
    cr.execute(
        """
        SELECT m.id
        FROM mrp_production m
        LEFT JOIN product_product p on m.product_id=p.id
        LEFT JOIN product_template pt ON p.product_tmpl_id=pt.id
        WHERE NOT pt.uom_id=m.product_uom_id
    """
    )
    ids = [x[0] for x in cr.fetchall()]
    util.recompute_fields(cr, "mrp.production", ["product_uom_qty"], ids=ids)

    cr.execute(
        """
        UPDATE mrp_workcenter_productivity_loss m
        SET loss_id=t.id
        FROM mrp_workcenter_productivity_loss_type t
        WHERE m.loss_type=t.loss_type
    """
    )
