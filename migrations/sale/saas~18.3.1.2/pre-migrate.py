from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.config.settings", "module_sale_gelato", "sale_gelato", "sale")
    util.remove_field(cr, "sale.order.discount", "tax_ids")
