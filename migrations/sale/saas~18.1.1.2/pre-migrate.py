from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.advance.payment.inv", "amount_to_invoice")
    util.remove_field(cr, "sale.advance.payment.inv", "display_invoice_amount_warning")
    util.rename_field(cr, "sale.order.line", "product_uom", "product_uom_id")
    util.rename_field(cr, "sale.report", "product_uom", "product_uom_id")
    util.rename_field(cr, "sale.order.line", "tax_id", "tax_ids")

    util.remove_field(cr, "sale.order.line", "product_packaging_id")
    util.remove_field(cr, "sale.order.line", "product_packaging_qty")
    util.remove_field(cr, "sale.order.line", "product_uom_category_id")

    util.remove_record(cr, "sale.menu_product_uom_categ_form_action")
    util.remove_record(cr, "sale.next_id_16")
