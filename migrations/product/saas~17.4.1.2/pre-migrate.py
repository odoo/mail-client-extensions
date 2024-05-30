from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "product_template", "service_tracking"):
        util.move_field_to_module(cr, "product.template", "service_tracking", "sale", "product")
    else:
        util.create_column(cr, "product_template", "service_tracking", "varchar", default="no")
