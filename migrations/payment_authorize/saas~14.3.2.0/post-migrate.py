from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    cr.execute(
        """
        UPDATE payment_acquirer
           SET inline_form_view_id = %s,
               support_authorization = True,
               support_tokenization = True,
               allow_tokenization = True
         WHERE "provider" = 'authorize'
        """,
        [util.ref(cr, "payment_authorize.inline_form")],
    )
