from odoo.upgrade import util


def migrate(cr, version):
    vid = util.ref(cr, "payment_razorpay.redirect_form")
    cr.execute(
        """
        UPDATE payment_provider
           SET redirect_form_view_id = NULL
         WHERE code = 'razorpay'
           AND redirect_form_view_id = %s
        """,
        [vid],
    )
    util.remove_view(cr, "payment_razorpay.redirect_form")
