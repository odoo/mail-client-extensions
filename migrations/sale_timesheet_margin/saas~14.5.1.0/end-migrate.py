from odoo.upgrade import util


def migrate(cr, version):
    query = """
        SELECT sol.id
          FROM sale_order_line sol
         WHERE sol.qty_delivered_method = 'timesheet'
        """
    util.recompute_fields(cr, "sale.order.line", ["purchase_price"], query=query)
