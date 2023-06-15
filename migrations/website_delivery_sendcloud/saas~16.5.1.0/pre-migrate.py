from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "delivery_carrier", "sendcloud_can_customize_use_locations", "bool")
    # As all delivery carrier based on sendcloud were reset, enforce false sendcloud_use_locations
    cr.execute(
        """
            UPDATE delivery_carrier
               SET sendcloud_use_locations = FALSE
             WHERE delivery_type = 'sendcloud'
        """,
    )
