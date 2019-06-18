# -*- coding: utf-8 -*-
import logging
from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.product.'
_logger = logging.getLogger(NS + __name__)

MINIMUM_ROUNDING = 1e-06

def migrate(cr, version):

    # hardcode some fk to uom.
    # we may use util.get_fk() but we also need the name of the `quantity` column
    uom_refs = [
        ('account_analytic_line', 'product_uom_id', 'unit_amount'),
        ('account_invoice_line', 'uos_id', 'quantity'),
        ('account_move_line', 'product_uom_id', 'quantity'),
        ('hr_expense_line', 'uom_id', 'unit_quantity'),
        ('mrp_bom_line', 'product_uom', 'product_qty'),
        ('mrp_bom', 'product_uom', 'product_qty'),
        ('mrp_production_product_line', 'product_uom', 'product_qty'),
        ('procurement_order', 'product_uom', 'product_qty'),
        ('purchase_order_line', 'product_uom', 'product_qty'),
        ('sale_order_line', 'product_uom', 'product_uom_qty'),
        ('sale_order_option', 'uom_id', 'quantity'),
        ('sale_quote_line', 'product_uom_id', 'product_uom_qty'),
        ('sale_quote_option', 'uom_id', 'quantity'),
        ('stock_inventory_line', 'product_uom_id', 'product_qty'),
        ('stock_move', 'product_uom', 'product_uom_qty'),
        ('stock_pack_operation', 'product_uom_id', 'product_qty'),
    ]

    query = """
        SELECT {uom} AS uom, {qty} AS qty
          FROM {tbl}
         WHERE {uom} IS NOT NULL
           AND {qty} IS NOT NULL
    """
    uom_usages = ' UNION '.join(
        query.format(tbl=tbl, uom=uom, qty=qty)
        for tbl, uom, qty in uom_refs
        if util.column_exists(cr, tbl, uom) and util.column_exists(cr, tbl, qty)
    )

    if uom_usages:
        cr.execute("""
            WITH uom_usages AS (
                {uom_usages}
            ),
            new_roundings AS (
                SELECT uom.id AS id,
                       coalesce(pow(10, -max(
                            char_length(split_part(trim(both '0' from uu.qty::varchar),
                                                   '.', 2)))), 1) AS new_rounding
                  FROM product_uom uom
             LEFT JOIN uom_usages uu ON (uu.uom = uom.id)
                 WHERE uom.rounding = 0
              GROUP BY uom.id
            )
            UPDATE product_uom u
               SET rounding = n.new_rounding
              FROM new_roundings n
             WHERE n.id = u.id
            RETURNING u.id, n.new_rounding
        """.format(uom_usages=uom_usages))
        for uom_id, new_rounding in cr.fetchall():
            _logger.warn("[UoM %s rounding adjusted to %s] rounding was 0", uom_id, new_rounding)
            assert new_rounding >= MINIMUM_ROUNDING, \
                "UoM's rounding adjustment too small, manual check required"

    cr.execute("UPDATE product_uom SET rounding = 0.01 WHERE rounding = 0 RETURNING id")
    for uom_id, in cr.fetchall():
        _logger.warn("[UoM %s rounding adjusted to 0.01] rounding was 0", uom_id)
