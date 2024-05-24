from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE product_template
           SET service_tracking = 'event'
         WHERE type='event'
        """,
        table="product_template",
    )
    util.change_field_selection_values(cr, "product.template", "type", {"event": "service"})
