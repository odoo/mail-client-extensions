from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.config.settings", "module_sale_gelato", "sale_gelato", "sale")
    util.remove_field(cr, "sale.order.discount", "tax_ids")

    util.rename_xmlid(cr, *util.expand_braces("sale.{,send_pending_emails_}cron"))

    util.remove_field(cr, "res.partner", "sale_warn")
    util.remove_field(cr, "product.template", "sale_line_warn")
