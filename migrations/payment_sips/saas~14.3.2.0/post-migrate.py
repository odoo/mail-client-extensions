from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    cr.execute(
        """
        UPDATE payment_acquirer
           SET redirect_form_view_id = %s
         WHERE "provider" = 'sips'
        """,
        [util.ref(cr, "payment_sips.redirect_form")],
    )
