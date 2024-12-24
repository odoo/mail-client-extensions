from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "stock.track.confirmation")
    util.remove_model(cr, "stock.track.line")
    util.remove_field(cr, "stock.warehouse", "crossdock_route_id")
    query = """
        UPDATE stock_quant sq
            SET inventory_diff_quantity = 0
        WHERE inventory_quantity_set IS NOT TRUE
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_quant", alias="sq"))
    util.remove_model(cr, "stock.change.product.qty")
    util.remove_view(cr, "stock.product_product_view_form_easy_inherit_stock")
