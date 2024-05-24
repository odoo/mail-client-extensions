from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE product_template
           SET service_tracking = 'event_booth'
         WHERE type = 'event_booth'
        """,
        table="product_template",
    )
    util.change_field_selection_values(cr, "product.template", "type", {"event_booth": "service"})
