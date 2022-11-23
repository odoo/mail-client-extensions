from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO payment_currency_rel
             SELECT ID,authorize_currency_id
               FROM payment_provider
              WHERE code='authorize'
                AND authorize_currency_id IS NOT NULL;
    """
    )
    util.remove_field(cr, "payment.provider", "authorize_currency_id")
