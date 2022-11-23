from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE payment_provider
           SET fees_dom_var = fees_dom_var / 100,
               fees_int_var = fees_int_var / 100;
    """
    )
    util.create_m2m(
        cr, "payment_currency_rel", "payment_provider", "res_currency", "payment_provider_id", "currency_id"
    )
