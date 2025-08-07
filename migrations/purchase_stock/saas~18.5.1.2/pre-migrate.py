from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "purchase_stock.view_category_property_form")
    util.remove_view(cr, "purchase_stock.product_template_form_view")
    util.remove_field(cr, "product.template", "property_account_creditor_price_difference")
    util.remove_field(cr, "product.category", "property_account_creditor_price_difference_categ")
