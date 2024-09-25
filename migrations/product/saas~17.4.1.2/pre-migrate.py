from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "product_template", "service_tracking"):
        util.move_field_to_module(cr, "product.template", "service_tracking", "sale", "product")
    else:
        util.create_column(cr, "product_template", "service_tracking", "varchar", default="no")
    util.remove_record(cr, "product.pricelist_availability")
    util.remove_record(cr, "product.pricelist_discounts")
    util.remove_field(cr, "res.config.settings", "group_sale_pricelist")
    util.remove_field(cr, "res.config.settings", "product_pricelist_setting")
    util.remove_field(cr, "product.pricelist", "discount_policy")

    util.create_column(cr, "product_pricelist_item", "price_markup", "float8")
    util.explode_execute(
        cr,
        """
        UPDATE product_pricelist_item
           SET price_markup = -price_discount
         WHERE base = 'standard_price'
        """,
        table="product_pricelist_item",
    )
    util.create_column(cr, "product_pricelist_item", "display_applied_on", "varchar", default="1_product")
    util.explode_execute(
        cr,
        """
        UPDATE product_pricelist_item
           SET display_applied_on = '2_product_category'
         WHERE applied_on = '2_product_category'
        """,
        table="product_pricelist_item",
    )
