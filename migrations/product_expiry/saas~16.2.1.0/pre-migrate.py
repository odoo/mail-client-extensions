from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("product_expiry.view_stock_quant_tree{_expiry,}"))
    util.rename_xmlid(cr, *eb("product_expiry.view_stock_quant_tree_editable{_expiry,}"))

    # Updates quants for products using expiration date to add the `expiration_date` on the quants.
    util.create_column(cr, "stock_quant", "expiration_date", "timestamp")
    query = """
        UPDATE stock_quant AS qt
           SET expiration_date = lot.expiration_date
          FROM stock_lot AS lot
         WHERE qt.lot_id = lot.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_quant", alias="qt"))
