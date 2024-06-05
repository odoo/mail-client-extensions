from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE payment_provider
           SET inline_form_view_id = %s,
               allow_tokenization = true
         WHERE code = 'xendit'
        """,
        [util.ref(cr, "payment_xendit.inline_form")],
    )
