from textwrap import dedent

from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    cr.execute(
        """
        UPDATE payment_acquirer
           SET inline_form_view_id = %s,
               support_tokenization = True,
               allow_tokenization = True
         WHERE "provider" = 'adyen'
        """,
        [util.ref(cr, "payment_adyen.inline_form")],
    )
    if cr.rowcount:
        msg = """
              You will need to reconfigure your Adyen providers.
              To be able to reconfigure Adyen providers, you have to follow [https://www.odoo.com/documentation/15.0/applications/general/payment_acquirers/adyen.html](the tutorial in the Odoo documentation).
              """  # noqa: B950
        util.add_to_migration_reports(dedent(msg.strip()), "Payment Providers")
