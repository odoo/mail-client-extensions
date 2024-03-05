from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "product_attribute_value", "product_attribute_value_value_company_uniq")
