from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_template", "allow_prorated_price", "boolean", default=False)

    query = """
        UPDATE product_template
           SET allow_prorated_price = true
         WHERE type = 'service'
           AND recurring_invoice = true
           AND invoice_policy != 'delivery'
        """

    util.explode_execute(cr, query, table="product_template")
