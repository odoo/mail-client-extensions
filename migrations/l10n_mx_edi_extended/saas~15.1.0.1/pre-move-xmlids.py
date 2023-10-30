def migrate(cr, version):
    # Move external ids of city in the right module in case they were in the wrong one
    cr.execute(
        """
        UPDATE ir_model_data
          SET module = 'l10n_mx_edi_extended'
        WHERE module = 'l10n_mx_edi'
          AND model = 'res.city'
        """
    )
