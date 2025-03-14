from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_property(cr, "product.template", "service_to_purchase", "boolean")
    util.remove_constraint(cr, "product_template", "product_template_service_to_purchase")
