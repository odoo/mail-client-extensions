from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_margin.sale_margin_sale_order_line")
    util.remove_view(cr, "sale_margin.sale_margin_sale_order_line_form")
