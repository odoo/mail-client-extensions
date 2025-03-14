from odoo.upgrade import util


def migrate(cr, version):
    field_name_list = [
        "delivered_price_subtotal",
        "delivered_price_tax",
        "delivered_price_total",
    ]
    for field_name in field_name_list:
        util.move_field_to_module(cr, "sale.order.line", field_name, "industry_fsm_sale_report", "industry_fsm_sale")
