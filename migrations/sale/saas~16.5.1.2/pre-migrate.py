from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_document", "attached_on", "varchar")
    if util.column_exists(cr, "ir_attachment", "product_downloadable"):
        query = """
        INSERT INTO product_document (ir_attachment_id, active, attached_on)
             SELECT ia.id,
                    TRUE,
                    CASE WHEN ia.product_downloadable THEN 'sale_order' ELSE NULL END
               FROM ir_attachment ia
              WHERE ia.res_model IN ('product.template', 'product.product')
                AND ia.res_field IS NULL
        """
        util.explode_execute(cr, query, table="ir_attachment", alias="ia")

        util.remove_field(cr, "ir.attachment", "product_downloadable")
    else:
        util.explode_execute(
            cr,
            """
            INSERT INTO product_document (ir_attachment_id, active)
            SELECT id, TRUE
              FROM ir_attachment
             WHERE ir_attachment.res_model IN ('product.template','product.product')
               AND ir_attachment.res_field IS NULL
            """,
            table="ir_attachment",
        )
    util.remove_field(cr, "product.template", "visible_qty_configurator")
    util.remove_field(cr, "payment.link.wizard", "show_confirmation_message")

    util.create_column(cr, "sale_order", "journal_id", "int4", fk_table="account_journal", on_delete_action="RESTRICT")
    util.create_column(cr, "sale_order", "prepayment_percent", "float8", default=1.0)
    util.create_column(cr, "res_company", "prepayment_percent", "float8", default=1.0)

    util.remove_view(cr, "sale.payment_checkout_inherit")
    util.remove_view(cr, "sale.payment_manage_inherit")

    util.rename_xmlid(cr, "sale.report_saleorder", "sale.report_saleorder_raw")
