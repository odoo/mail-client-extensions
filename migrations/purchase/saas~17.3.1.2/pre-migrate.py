from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "purchase.view_product_account_purchase_ok_form")
    util.create_column(cr, "purchase_order", "amount_total_cc", "numeric")
    util.explode_execute(
        cr,
        """
        UPDATE purchase_order
            SET amount_total_cc = amount_total / COALESCE(NULLIF(currency_rate, 0), 1.0)
        """,
        table="purchase_order",
    )
