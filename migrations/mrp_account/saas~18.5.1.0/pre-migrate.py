from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp_account.view_category_property_form")
