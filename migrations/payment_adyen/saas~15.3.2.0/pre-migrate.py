from odoo.upgrade import util


def migrate(cr, version):
    if util.version_gte("saas~15.4"):
        return

    cr.execute("UPDATE payment_acquirer SET support_authorization = TRUE WHERE provider = 'adyen'")
