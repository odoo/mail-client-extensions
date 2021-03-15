def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    cr.execute(
        """
        UPDATE payment_acquirer
           SET support_tokenization = True,
               allow_tokenization = True
         WHERE "provider" = 'stripe'
        """
    )
