from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE payment_provider
           SET inline_form_view_id = %s
         WHERE code = 'stripe'
        """,
        [util.ref(cr, "payment_stripe.inline_form")],
    )
