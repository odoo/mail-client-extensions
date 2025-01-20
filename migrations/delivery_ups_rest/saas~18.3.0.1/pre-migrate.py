from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            UPDATE delivery_carrier
               SET allow_cash_on_delivery = TRUE
             WHERE delivery_type = 'ups_rest'
               AND ups_cod = TRUE
        """
    )
    util.remove_field(cr, "delivery.carrier", "ups_cod")
