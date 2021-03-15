from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    cr.execute(
        """
        UPDATE payment_acquirer
           SET redirect_form_view_id = %s
         WHERE "provider" = 'transfer'
        """,
        [util.ref(cr, "payment_transfer.redirect_form")],
    )
