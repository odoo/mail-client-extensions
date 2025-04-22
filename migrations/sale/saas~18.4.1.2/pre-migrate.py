from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "product.category", "property_account_downpayment_categ_id")
    util.remove_view(cr, "sale.view_category_property_form")
