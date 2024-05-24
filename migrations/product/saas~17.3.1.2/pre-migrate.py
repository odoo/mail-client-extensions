from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "product_attribute_value", "product_attribute_value_value_company_uniq")
    util.update_field_usage(cr, "product.template", "type", "detailed_type")
    util.remove_field(cr, "product.template", "type")
    util.rename_field(cr, "product.template", "detailed_type", "type")
