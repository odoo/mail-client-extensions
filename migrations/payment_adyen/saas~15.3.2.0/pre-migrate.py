def migrate(cr, version):
    cr.execute("UPDATE payment_acquirer SET support_authorization = TRUE WHERE provider = 'adyen'")
