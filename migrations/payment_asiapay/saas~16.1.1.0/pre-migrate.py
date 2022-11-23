from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO payment_currency_rel
             SELECT ID,asiapay_currency_id
               FROM payment_provider
              WHERE code='asiapay'
                AND asiapay_currency_id IS NOT NULL;
    """
    )
    util.remove_field(cr, "payment.provider", "asiapay_currency_id")
