from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            UPDATE delivery_carrier
               SET allow_cash_on_delivery = TRUE
             WHERE delivery_type = 'shiprocket'
               AND shiprocket_payment_method = 'cod'
        """
    )
    util.remove_field(cr, "delivery.carrier", "shiprocket_payment_method")
