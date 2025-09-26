from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/odoo/pull/126804
    util.create_column(cr, "purchase_order_line", "discount", "numeric", default=0)
