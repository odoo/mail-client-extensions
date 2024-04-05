from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.quant", "priority")
    util.rename_xmlid(cr, "stock.stock_location_inter_wh", "stock.stock_location_inter_company")

    query = """
        WITH default_company_locs AS (
               SELECT sw.company_id,
                      (array_agg(sw.lot_stock_id ORDER BY sw.id))[1] AS lot_stock_id
                 FROM stock_warehouse sw
                WHERE sw.active = True
             GROUP BY sw.company_id
        ),
        external_locs AS (
               SELECT sl.company_id,
                      (array_agg(sl.id ORDER BY sl.active DESC, sl.id))[1] AS id
                 FROM stock_location sl
                WHERE sl.usage = %s
             GROUP BY sl.company_id
        )
        UPDATE stock_picking_type spt
           SET {default_location_field} = CASE WHEN spt.code IN %s THEN COALESCE(%s, cel.id, nel.id)
                                               ELSE COALESCE(sw.lot_stock_id, dcl.lot_stock_id)
                                           END
          FROM stock_picking_type spt2
     LEFT JOIN stock_warehouse sw
            ON spt2.warehouse_id = sw.id
          JOIN default_company_locs dcl
            ON spt2.company_id = dcl.company_id
     LEFT JOIN external_locs nel
            ON nel.company_id IS NULL
     LEFT JOIN external_locs cel
            ON spt2.company_id = cel.company_id
         WHERE spt.{default_location_field} IS NULL
           AND spt.id = spt2.id
    """

    # Add default destination to either Customers or Warehouse/Stock
    customer_id = util.ref(cr, "stock.stock_location_customers")
    cr.execute(
        util.format_query(cr, query, default_location_field="default_location_dest_id"),
        ["customer", ("outgoing", "dropship"), customer_id],
    )

    # Add default source to either Vendors or Warehouse/Stock
    vendor_id = util.ref(cr, "stock.stock_location_suppliers")
    cr.execute(
        util.format_query(cr, query, default_location_field="default_location_src_id"),
        ["supplier", ("incoming", "dropship"), vendor_id],
    )
