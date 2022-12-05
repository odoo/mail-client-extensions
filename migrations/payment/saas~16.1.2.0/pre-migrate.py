def migrate(cr, version):
    cr.execute(
        """
        UPDATE payment_provider
           SET fees_dom_var = fees_dom_var / 100,
               fees_int_var = fees_int_var / 100;
    """
    )
