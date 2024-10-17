from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "purchase_order_line", "state")
    util.remove_column(cr, "purchase_order_line", "currency_id")
    util.rename_field(cr, "purchase.order.line", "product_uom", "product_uom_id")
    util.rename_field(cr, "purchase.report", "product_uom", "product_uom_id")

    util.remove_field(cr, "purchase.order.line", "product_packaging_id")
    util.remove_field(cr, "purchase.order.line", "product_packaging_qty")
    util.remove_field(cr, "purchase.order.line", "product_uom_category_id")

    util.remove_view(cr, "purchase.product_view_kanban_catalog_purchase_only")
    util.remove_view(cr, "purchase.product_packaging_form_view_purchase")
    util.remove_view(cr, "purchase.product_packaging_tree_view_purchase")
    util.remove_record(cr, "purchase.menu_purchase_uom_categ_form_action")
    util.remove_record(cr, "purchase.menu_unit_of_measure_in_config_purchase")
