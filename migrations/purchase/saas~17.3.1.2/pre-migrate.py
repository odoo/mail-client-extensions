from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "purchase.view_product_account_purchase_ok_form")
