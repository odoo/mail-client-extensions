from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE payment_acquirer SET support_authorization = TRUE WHERE provider = 'stripe'")

    if cr.rowcount:
        util.add_to_migration_reports(
            "Odoo is now listening to other events coming from the payment provider Stripe. In order to configure this, please "
            "follow the following documentation: "
            "https://www.odoo.com/documentation/saas-15.3/applications/finance/payment_acquirers/stripe.html#webhook-signing-secret"
        )
