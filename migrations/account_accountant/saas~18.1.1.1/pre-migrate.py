from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_accountant.product_template_form_view")
