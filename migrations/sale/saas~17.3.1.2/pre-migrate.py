from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale.sale_order_view_form")
