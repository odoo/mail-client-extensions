from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE pos_config c
           SET settle_invoice_product_id = %s
         WHERE c.settle_invoice_product_id IS NULL
           AND NOT EXISTS(
                SELECT 1
                  FROM pos_session s
                 WHERE s.config_id = c.id
                   AND (s.rescue OR s.state IN ('opened', 'closing_control'))
               )
        """,
        [util.ref(cr, "pos_settle_due.product_product_settle_invoice")],
    )
