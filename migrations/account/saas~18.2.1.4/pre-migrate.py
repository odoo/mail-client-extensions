from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account.product_template_view_tree")
