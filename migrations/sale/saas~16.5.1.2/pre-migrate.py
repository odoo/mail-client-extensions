from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_document", "attached_on", "varchar")
    if util.column_exists(cr, "ir_attachment", "product_downloadable"):
        cr.execute(
            """
        INSERT INTO product_document (ir_attachment_id, active, attached_on)
             SELECT ia.id,
                    TRUE,
                    'sale_order'
               FROM ir_attachment ia
              WHERE ia.res_model IN ('product.template', 'product.product')
                AND ia.product_downloadable
        """
        )

        util.remove_field(cr, "ir.attachment", "product_downloadable")

    util.remove_field(cr, "product.template", "visible_qty_configurator")
    util.remove_field(cr, "payment.link.wizard", "show_confirmation_message")
    util.create_column(cr, "sale_order", "prepayment_percent", "numeric", default=1.0)
    util.create_column(cr, "res_company", "prepayment_percent", "numeric", default=1.0)

    util.remove_view(cr, "sale.payment_checkout_inherit")
    util.remove_view(cr, "sale.payment_manage_inherit")
