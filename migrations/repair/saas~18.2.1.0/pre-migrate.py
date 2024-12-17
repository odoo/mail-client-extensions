from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE product_template
           SET service_tracking = 'repair'
         WHERE type = 'service'
           AND create_repair IS TRUE
        """
    )
    util.remove_field(cr, "product.template", "create_repair")
