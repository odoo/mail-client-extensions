from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "purchase_stock.view_category_property_form")
    util.remove_view(cr, "purchase_stock.product_template_form_view")
    util.remove_field(cr, "product.template", "property_account_creditor_price_difference")
    util.remove_field(cr, "product.category", "property_account_creditor_price_difference_categ")
    util.remove_view(cr, "purchase_stock.purchase_order_suggest_view_form")
    util.remove_field(cr, "stock.warehouse.orderpoint", "vendor_id")
    util.remove_field(cr, "stock.warehouse.orderpoint", "purchase_visibility_days")
    util.remove_model(cr, "purchase.order.suggest")
    util.create_column(cr, "res_partner", "suggest_based_on", "varchar", default="30_days")
    util.create_column(cr, "res_partner", "suggest_days", "int4", default=7)
    util.create_column(cr, "res_partner", "suggest_percent", "int4", default=100)
