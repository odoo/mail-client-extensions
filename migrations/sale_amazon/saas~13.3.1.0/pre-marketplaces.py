from odoo.upgrade import util

def migrate(cr, version):
    util.create_column(cr, "amazon_marketplace", "tax_included", "bool")
    cr.execute(
        """
        UPDATE amazon_marketplace
        SET tax_included = true
        WHERE api_ref IN (
            'A1PA6795UKMFR9', 'A1RKKUPIHCS9HS', 'A13V1IB3VIYZZH', 'APJ6JRA9NG5V4', 'A1F83G8C2ARO7P'
        )
        """
    )
    cr.execute("UPDATE amazon_marketplace SET tax_included=FALSE WHERE tax_included IS NULL")
