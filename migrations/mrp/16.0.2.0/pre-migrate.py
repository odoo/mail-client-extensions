from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp.report_mrp_bom_line")
    util.remove_view(cr, "mrp.report_mrp_operation_line")
    util.remove_view(cr, "mrp.report_mrp_byproduct_line")
    util.remove_view(cr, "mrp.report_mrp_bom_pdf")

    util.create_column(cr, "mrp_bom_line", "manual_consumption", "boolean", default=False)
    cr.execute(
        """
            UPDATE mrp_bom_line line
               SET manual_consumption = true
              FROM product_product p
              JOIN product_template pt
                ON p.product_tmpl_id = pt.id
             WHERE p.id = line.product_id
               AND pt.tracking != 'none'
        """
    )

    util.create_column(cr, "stock_picking_type", "use_auto_consume_components_lots", "boolean", default=False)
    util.create_column(cr, "stock_move", "manual_consumption", "boolean", default=False)
    query = """
        UPDATE stock_move AS move
           SET manual_consumption = true
          FROM stock_move m
          JOIN product_product p
            ON p.id = m.product_id
          JOIN product_template pt
            ON pt.id = p.product_tmpl_id
          JOIN mrp_bom_line bom
            ON bom.id = m.bom_line_id
         WHERE m.state = 'draft'
           AND m.id = move.id
           AND (bom.manual_consumption OR pt.tracking != 'none')
           AND {parallel_filter}
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_move", alias="move"))
