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
