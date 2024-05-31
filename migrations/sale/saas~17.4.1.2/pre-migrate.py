from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "website_sale"):
        util.move_field_to_module(cr, "sale.order.line", "linked_line_id", "website_sale", "sale")
        util.move_field_to_module(cr, "sale.order.line", "option_line_ids", "website_sale", "sale")
        util.rename_field(cr, "sale.order.line", "option_line_ids", "linked_line_ids")
