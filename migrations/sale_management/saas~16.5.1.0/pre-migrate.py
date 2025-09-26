from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order_template", "prepayment_percent", "float8", default=1.0)
    util.remove_field(cr, "res.config.settings", "module_sale_quotation_builder")
    util.move_field_to_module(cr, "sale.order.template", "journal_id", "sale_subscription", "sale_management")
