def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_model_data
           SET module = 'l10n_br'
         WHERE module = 'l10n_br_avatax'
           AND model = 'res.city'
        """
    )
