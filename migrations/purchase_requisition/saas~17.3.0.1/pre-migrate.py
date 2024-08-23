from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order_line", "price_total_cc", "numeric")
    util.explode_execute(
        cr,
        """
        UPDATE purchase_order_line AS pol
           SET price_total_cc = pol.price_subtotal / COALESCE(NULLIF(po.currency_rate, 0), 1.0)
          FROM purchase_order po
         WHERE pol.order_id = po.id
        """,
        table="purchase_order_line",
        alias="pol",
    )
