from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    cr.execute(
        """
        UPDATE payment_acquirer
           SET redirect_form_view_id = %s,
               support_fees_computation = True
         WHERE "provider" = 'paypal'
        """,
        [util.ref(cr, "payment_paypal.redirect_form")],
    )
