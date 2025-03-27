from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.product_variants")
    cr.execute(
        "UPDATE ir_ui_view SET customize_show = FALSE WHERE id = %s",
        [util.ref(cr, "website_sale.product_custom_text")],
    )
    util.remove_view(cr, "website_sale.sale_order_view_form_cart_recovery")
    util.remove_view(cr, "website_sale.cart_item_line_heading")
