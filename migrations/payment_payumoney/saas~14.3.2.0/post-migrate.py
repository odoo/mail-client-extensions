from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    cr.execute(
        """
        UPDATE payment_acquirer
           SET redirect_form_view_id = %s
         WHERE "provider" = 'payumoney'
        """,
        [util.ref(cr, "payment_payumoney.redirect_form")],
    )
