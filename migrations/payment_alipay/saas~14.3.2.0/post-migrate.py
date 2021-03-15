from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    cr.execute(
        """
        UPDATE payment_acquirer
           SET redirect_form_view_id = %s,
               support_fees_computation = True
         WHERE "provider" = 'alipay'
        """,
        [util.ref(cr, "payment_alipay.redirect_form")],
    )
