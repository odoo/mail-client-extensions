from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            UPDATE delivery_carrier
               SET allow_cash_on_delivery = TRUE
             WHERE delivery_type = 'ups'
               AND ups_cod = TRUE
        """
    )
    # Keep column, may be needed in delivery_ups_rest/saas~18.3.0.1/pre-migrate.py
    util.remove_field(cr, "delivery.carrier", "ups_cod", drop_column=False)
