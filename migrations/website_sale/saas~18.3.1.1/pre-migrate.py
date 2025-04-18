from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.product_variants")
    util.remove_view(cr, "website_sale.product_share_buttons")
    cr.execute(
        "UPDATE ir_ui_view SET customize_show = FALSE WHERE id = %s",
        [util.ref(cr, "website_sale.product_custom_text")],
    )
    util.remove_view(cr, "website_sale.sale_order_view_form_cart_recovery")
    util.remove_view(cr, "website_sale.cart_item_line_heading")
    util.remove_view(cr, "website_sale.add_grid_or_list_option")
    util.remove_field(cr, "website", "prevent_zero_price_sale_text")
    util.remove_view(cr, "website_sale.crm_team_view_kanban_dashboard")
    util.rename_xmlid(cr, "website_sale.o_wsale_offcanvas_color_attribute", "website_sale.filter_color_attributes")
