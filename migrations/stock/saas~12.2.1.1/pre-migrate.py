# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "stock.view_stock_level_forecast_graph")
    cr.execute("ALTER TABLE res_config_settings ALTER COLUMN module_procurement_jit TYPE varchar")
    cr.execute("ALTER TABLE stock_quantity_history ALTER COLUMN compute_at_date TYPE varchar")

    util.create_column(cr, "stock_move", "description_picking", "text")
    util.create_column(cr, "stock_move_line", "description_picking", "text")

    # XXX description_picking{in,out} being translatable, do we need to fill this fields?
    # TODO copy translations?
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        UPDATE stock_move m
           SET description_picking = COALESCE(CASE t.code WHEN 'incoming' THEN e.description_pickingin
                                                          WHEN 'outgoing' THEN e.description_pickingout
                                                          WHEN 'internal' THEN e.description_picking
                                               END, e.description, e.name)
          FROM product_product p, product_template e, stock_picking_type t
         WHERE p.id = m.product_id
           AND e.id = p.product_tmpl_id
           AND t.id = m.picking_type_id
        """,
            table="stock_move",
            prefix="m.",
        ),
    )
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        UPDATE stock_move_line l
           SET description_picking = COALESCE(CASE t.code WHEN 'incoming' THEN e.description_pickingin
                                                          WHEN 'outgoing' THEN e.description_pickingout
                                                          WHEN 'internal' THEN e.description_picking
                                               END, e.description, e.name)
          FROM product_product p, product_template e, stock_picking k, stock_picking_type t
         WHERE p.id = l.product_id
           AND e.id = p.product_tmpl_id
           AND k.id = l.picking_id
           AND t.id = k.picking_type_id
        """,
            table="stock_move_line",
            prefix="l.",
        ),
    )
