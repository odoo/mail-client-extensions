from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order_line", "product_description_variants", "varchar")
    util.create_column(cr, "purchase_order", "effective_date", "timestamp without time zone")

    cr.execute(
        """
        WITH pol AS (
                SELECT po.id, MIN(s.date_done) as date_done
                  FROM purchase_order po
                  JOIN purchase_order_stock_picking_rel r ON (po.id = r.purchase_order_id)
                  JOIN stock_picking s ON (s.id = r.stock_picking_id)
              GROUP BY po.id
        )
        UPDATE purchase_order po
           SET effective_date = pol.date_done
          FROM pol
         WHERE po.id = pol.id
           AND pol.date_done IS NOT NULL
    """
    )

    util.remove_record(cr, "purchase_stock.access_stock_location_purchase_manager")
    util.remove_record(cr, "purchase_stock.purchase_open_picking")
