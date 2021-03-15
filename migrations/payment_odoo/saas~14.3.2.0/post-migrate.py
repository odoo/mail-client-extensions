from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    cr.execute(
        """
        UPDATE payment_acquirer
           SET redirect_form_view_id = %s,
               support_tokenization = True,
               allow_tokenization = True
         WHERE "provider" = 'odoo'
        """,
        [util.ref(cr, "payment_odoo.redirect_form")],
    )
