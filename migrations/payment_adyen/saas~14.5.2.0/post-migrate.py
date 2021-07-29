def migrate(cr, version):
    cr.execute(
        """
        UPDATE payment_acquirer
           SET support_refund = 'partial'
         WHERE "provider" = 'adyen'
        """
    )
