from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_ui_view
           SET customize_show = FALSE
         WHERE id IN %s
        """,
        [
            (
                util.ref(cr, "website_sale_wishlist.add_to_wishlist"),
                util.ref(cr, "website_sale_wishlist.product_add_to_wishlist"),
            )
        ],
    )
